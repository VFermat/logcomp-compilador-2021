import sys
from typing import List, NoReturn, Union
from enum import Enum
from tokens import Token, TokenTypes
from tokenizer import Tokenizer
from nodes import (
    Block,
    Assigner,
    Print,
    While,
    If,
    Readln,
    BinOp,
    UnOp,
    IdentifierVal,
    IntVal,
    NoOp,
    Node,
)
from symbolTable import SymbolTable


class PrePro:
    def filter(self, text: str) -> str:
        text = text.strip()
        text = text.replace("\n", " ")
        position: int = text.find("/*")
        while position != -1:
            end_position: int = text[position:].find("*/")
            if end_position != -1:
                text = text[:position] + text[position + end_position + 2 :]
            else:
                raise ValueError()
            position = text.find("/*")
        return text.strip()


class Parser:

    tokens: Tokenizer
    levelZeroTokens: List[TokenTypes] = [TokenTypes.PLUS, TokenTypes.MINUS]
    levelOneTokens: List[TokenTypes] = [TokenTypes.MULTIPLIER, TokenTypes.DIVIDER]
    variableTypes: List[str] = ['int', 'bool', 'var']
    reservedWords: List[str] = ["println"]
    openPars: int = 0
    openBlocks: int = 0
    symbols: SymbolTable

    def __init__(self, code: str):
        prepro = PrePro()
        code = prepro.filter(code)
        self.tokens = Tokenizer(code)
        self.symbols = SymbolTable()

    def parseBlock(self) -> Block:
        if self.tokens.actual.tokenType != TokenTypes.BLOCK_OPENER:
            raise BufferError("Block requires opener token `{`")
        block = Block(self.tokens.actual)
        self.openBlocks += 1
        self.tokens.selectNext()
        while self.tokens.actual.tokenType != TokenTypes.BLOCK_CLOSER:
            command = self.parseCommand()
            if command.value.value == 'else':
                raise BufferError(
                    f"Invalid position for Else statement."
                )
            block.addNode(command)
            if self.tokens.actual == TokenTypes.EOF:
                return block
            self.tokens.selectNext()
            if self.tokens.actual.value == 'else' and block.child[-1].value.value == 'if':
                block.child[-1].setCommandFalse(self.parseCommand())
                self.tokens.selectNext()
        self.openBlocks -= 1
        return block

    def parseCommand(self) -> Node:
        if self.tokens.actual.tokenType == TokenTypes.IDENTIFIER:
            identifier = self.tokens.actual
            self.tokens.selectNext()
            if identifier.value in self.variableTypes:
                variable = self.tokens.actual
                self.tokens.selectNext()
                if self.tokens.actual.tokenType == TokenTypes.SEPARATOR:
                    return Assigner(variable, NoOp(variable), identifier.value)
                elif self.tokens.actual.tokenType == TokenTypes.ASSIGN:
                    root = Assigner(variable, self.parseOrExpr(), identifier.value)
                    if self.tokens.actual.tokenType != TokenTypes.SEPARATOR:
                        raise BufferError(
                            "Invalid Token. Line should end with separator `;`"
                        )
                    return root
            elif identifier.value == "println":
                if self.tokens.actual.tokenType != TokenTypes.LPAR:
                    raise BufferError(
                        f"Invalid Token. {identifier.value} should be followed by LPAR token `(`"
                    )
                value = self.parseOrExpr()
                if self.tokens.actual.tokenType != TokenTypes.RPAR:
                    raise BufferError(
                        f"Invalid Token. {identifier.value} should be followed by RPAR token `)`"
                    )
                self.tokens.selectNext()
                if self.tokens.actual.tokenType != TokenTypes.SEPARATOR:
                    raise BufferError(
                        "Invalid Token. Line should end with separator `;`"
                    )
                return Print(identifier, value)
            elif identifier.value == "while":
                if self.tokens.actual.tokenType != TokenTypes.LPAR:
                    raise BufferError(
                        f"Invalid Token. {identifier.value} should be followed by LPAR token `(`"
                    )
                condition = self.parseOrExpr()
                if self.tokens.actual.tokenType != TokenTypes.RPAR:
                    raise BufferError(
                        f"Invalid Token. {identifier.value} should be followed by RPAR token `)`"
                    )
                self.tokens.selectNext()
                command = self.parseCommand()
                return While(identifier, condition, command)
            elif identifier.value == "if":
                if self.tokens.actual.tokenType != TokenTypes.LPAR:
                    raise BufferError(
                        f"Invalid Token. {identifier.value} should be followed by LPAR token `(`"
                    )
                condition = self.parseOrExpr()
                if self.tokens.actual.tokenType != TokenTypes.RPAR:
                    raise BufferError(
                        f"Invalid Token. {identifier.value} should be followed by RPAR token `)`"
                    )
                self.tokens.selectNext()
                command = self.parseCommand()
                block = If(identifier, condition, command)
                if (
                    self.tokens.actual.tokenType == TokenTypes.IDENTIFIER
                    and self.tokens.actual.value == "else"
                ):
                    self.tokens.selectNext()
                    elseCommand = self.parseCommand()
                    block.setCommandFalse(elseCommand)
                return block
            elif identifier.value == "else":
                command = self.parseCommand()
                command.value = identifier
                return command
            else:
                if self.tokens.actual.tokenType != TokenTypes.ASSIGN:
                    raise BufferError(
                        "Invalid Token. Identifier should be followed by assigner token `=`"
                    )
                root = Assigner(identifier, self.parseOrExpr())
                if self.tokens.actual.tokenType != TokenTypes.SEPARATOR:
                    raise BufferError(
                        "Invalid Token. Line should end with separator `;`"
                    )
                return root
        elif self.tokens.actual.tokenType == TokenTypes.SEPARATOR:
            self.tokens.selectNext()
            return NoOp(self.tokens.actual)
        elif self.tokens.actual.tokenType == TokenTypes.BLOCK_OPENER:
            return self.parseBlock()
        raise BufferError("Invalid line")

    def parseOrExpr(self) -> Node:
        node = self.parseAndExpr()
        root = BinOp(Token(TokenTypes.EOF, 0), node, NoOp(Token(TokenTypes.EOF, 0)))
        while self.tokens.actual.tokenType == TokenTypes.BOOL_OR:
            root.setValue(self.tokens.actual)
            root.setRight(self.parseAndExpr())
            tmp = BinOp(Token(TokenTypes.EOF, 0), root, NoOp(Token(TokenTypes.EOF, 0)))
            root = tmp
        root = root.children[0]
        return root

    def parseAndExpr(self) -> Node:
        node = self.parseEqExpr()
        root = BinOp(Token(TokenTypes.EOF, 0), node, NoOp(Token(TokenTypes.EOF, 0)))
        while self.tokens.actual.tokenType == TokenTypes.BOOL_AND:
            root.setValue(self.tokens.actual)
            root.setRight(self.parseEqExpr())
            tmp = BinOp(Token(TokenTypes.EOF, 0), root, NoOp(Token(TokenTypes.EOF, 0)))
            root = tmp
        root = root.children[0]
        return root

    def parseEqExpr(self) -> Node:
        node = self.parseRelExpr()
        root = BinOp(Token(TokenTypes.EOF, 0), node, NoOp(Token(TokenTypes.EOF, 0)))
        while self.tokens.actual.tokenType == TokenTypes.BOOL_EQUAL:
            root.setValue(self.tokens.actual)
            root.setRight(self.parseRelExpr())
            tmp = BinOp(Token(TokenTypes.EOF, 0), root, NoOp(Token(TokenTypes.EOF, 0)))
            root = tmp
        root = root.children[0]
        return root

    def parseRelExpr(self) -> Node:
        node = self.parseExpression()
        root = BinOp(Token(TokenTypes.EOF, 0), node, NoOp(Token(TokenTypes.EOF, 0)))
        while self.tokens.actual.tokenType in [TokenTypes.BOOL_GT, TokenTypes.BOOL_LT]:
            root.setValue(self.tokens.actual)
            root.setRight(self.parseExpression())
            tmp = BinOp(Token(TokenTypes.EOF, 0), root, NoOp(Token(TokenTypes.EOF, 0)))
            root = tmp
        root = root.children[0]
        return root

    def parseExpression(self) -> Node:
        node = self.parseTerm()
        root = BinOp(Token(TokenTypes.EOF, 0), node, NoOp(Token(TokenTypes.EOF, 0)))
        while self.tokens.actual.tokenType in self.levelZeroTokens:
            root.setValue(self.tokens.actual)
            root.setRight(self.parseTerm())
            tmp = BinOp(Token(TokenTypes.EOF, 0), root, NoOp(Token(TokenTypes.EOF, 0)))
            root = tmp
        root = root.children[0]
        return root

    def parseTerm(self) -> Node:
        node = self.parseFactor()
        root = BinOp(Token(TokenTypes.EOF, 0), node, NoOp(Token(TokenTypes.EOF, 0)))
        self.tokens.selectNext()
        while self.tokens.actual.tokenType in self.levelOneTokens:
            root.setValue(self.tokens.actual)
            root.setRight(self.parseFactor())
            tmp = BinOp(Token(TokenTypes.EOF, 0), root, NoOp(Token(TokenTypes.EOF, 0)))
            root = tmp
            self.tokens.selectNext()
        root = root.children[0]
        return root

    def parseFactor(self) -> Node:
        self.tokens.selectNext()
        if self.tokens.actual.tokenType == TokenTypes.NUMBER:
            return IntVal(self.tokens.actual)
        elif (
            self.tokens.actual.tokenType in self.levelZeroTokens
            or self.tokens.actual.tokenType == TokenTypes.BOOL_NOT
        ):
            return UnOp(self.tokens.actual, self.parseFactor())
        elif self.tokens.actual.tokenType == TokenTypes.RPAR:
            raise ValueError()
        elif self.tokens.actual.tokenType == TokenTypes.IDENTIFIER:
            if self.tokens.actual.value != "readln":
                return IdentifierVal(
                    Token(TokenTypes.IDENTIFIER, self.tokens.actual.value)
                )
            self.tokens.selectNext()
            if self.tokens.actual.tokenType != TokenTypes.LPAR:
                raise BufferError()
            self.tokens.selectNext()
            if self.tokens.actual.tokenType != TokenTypes.RPAR:
                raise BufferError()
            return Readln(self.tokens.actual)
        elif self.tokens.actual.tokenType == TokenTypes.LPAR:
            self.openPars += 1
            root = self.parseOrExpr()
            if self.tokens.actual.tokenType == TokenTypes.RPAR:
                self.openPars -= 1
        else:
            raise BufferError(
                f"Invalid token type on factor. {self.tokens.actual.tokenType}"
            )
        return root

    def run(self) -> NoReturn:
        self.tokens.selectNext()
        block = self.parseBlock()
        self.tokens.selectNext()
        if (
            self.openPars == 0
            and self.openBlocks == 0
            and self.tokens.actual.tokenType == TokenTypes.EOF
        ):
            block.evaluate(self.symbols)
        else:
            raise BufferError(
                f"Open Pars: {self.openPars} | Open Blocks: {self.openBlocks} | Last Token: {self.tokens.actual.tokenType}"
            )


if __name__ == "__main__":
    f = sys.argv[1]
    # f = "test.c"
    with open(f, "r") as tmp:
        sentence = tmp.read()
    parser = Parser(sentence)
    parser.run()
