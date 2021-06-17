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
    StrVal,
    BoolVal,
    FuncCall,
    FuncDef,
    Return,
)
from logger import Logger
from symbolTable import SymbolTable


class PrePro:
    def filter(self, text: str) -> str:
        text = text.strip()
        # text = text.replace("\n", " ")
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
    variableTypes: List[str] = ["int", "bool", "string"]
    openPars: int = 0
    openBlocks: int = 0
    symbols: SymbolTable
    logger: Logger

    def __init__(self, code: str, logger: Logger):
        prepro = PrePro()
        code = prepro.filter(code)
        self.tokens = Tokenizer(code)
        self.symbols = SymbolTable()
        self.logger = logger

    def parseFuncDefBlock(self) -> Block:
        block = Block(self.tokens.actual)
        while self.tokens.actual.value in self.variableTypes:
            self.tokens.selectNext()
            logger.logParse(
                f"[INFO] [FUNCBLOCK] Starting funcblock of name {self.tokens.actual.value}"
            )
            if self.tokens.actual.tokenType != TokenTypes.IDENTIFIER:
                raise BufferError("Function should be identified by name")
            func = FuncDef(self.tokens.actual)
            self.tokens.selectNext()
            if self.tokens.actual.tokenType != TokenTypes.LPAR:
                raise BufferError("Function name should be followed by Parenthesis")
            self.tokens.selectNext()
            while self.tokens.actual.tokenType != TokenTypes.RPAR:
                identifier = self.tokens.actual
                if identifier.value not in self.variableTypes:
                    raise BufferError("Argument should have a type")
                self.tokens.selectNext()
                variable = self.tokens.actual
                logger.logParse(
                    f"[INFO] [FUNCBLOCK] Adding arg to func. {identifier.value} {variable.value}"
                )
                func.addArgument(Assigner(variable, NoOp(variable), identifier.value))
                self.tokens.selectNext()
                if self.tokens.actual.tokenType == TokenTypes.COMMA:
                    self.tokens.selectNext()
            self.tokens.selectNext()
            func.addStatements(self.parseCommand())
            logger.logParse(f"[INFO] [FUNCBLOCK] End funcblock {func.value.value}")
            block.addNode(func)
            self.tokens.selectNext()
        return block

    def parseBlock(self) -> Block:
        if self.tokens.actual.tokenType != TokenTypes.BLOCK_OPENER:
            raise BufferError("Block requires opener token `{`")
        block = Block(self.tokens.actual)
        logger.logParse(f"[INFO] [BLOCK] Starting block")
        self.openBlocks += 1
        self.tokens.selectNext()
        while self.tokens.actual.tokenType != TokenTypes.BLOCK_CLOSER:
            command = self.parseCommand()
            if command.value.value == "else":
                raise BufferError(f"Invalid position for Else statement.")
            logger.logParse(
                f"[INFO] [BLOCK] New command parsed. Adding to Block. {type(command)}"
            )
            block.addNode(command)
            if self.tokens.actual == TokenTypes.EOF:
                return block
            self.tokens.selectNext()
            if (
                self.tokens.actual.value == "else"
                and block.children[-1].value.value == "if"
            ):
                logger.logParse(f"[INFO] [BLOCK] Find Else. Setting command false")
                block.children[-1].setCommandFalse(self.parseCommand())
                self.tokens.selectNext()
        self.openBlocks -= 1
        logger.logParse(f"[INFO] [BLOCK] Ending block")
        return block

    def parseCommand(self) -> Node:
        logger.logParse(f"[INFO] [COMMAND] Parsing new command.")
        if self.tokens.actual.tokenType == TokenTypes.IDENTIFIER:
            identifier = self.tokens.actual
            self.tokens.selectNext()
            if identifier.value in self.variableTypes:
                variable = self.tokens.actual
                logger.logParse(
                    f"[INFO] [COMMAND] Variable declaration. {identifier.value} {variable.value}"
                )
                self.tokens.selectNext()
                if self.tokens.actual.tokenType == TokenTypes.SEPARATOR:
                    return Assigner(variable, NoOp(variable), identifier.value)
                elif self.tokens.actual.tokenType == TokenTypes.ASSIGN:
                    root = Assigner(variable, self.parseOrExpr(), identifier.value)
                    logger.logParse(f"[INFO] [COMMAND] Set Variable. {root.child}")
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
                logger.logParse(f"[INFO] [COMMAND] Println. {value}")
                if self.tokens.actual.tokenType != TokenTypes.RPAR:
                    raise BufferError(
                        f"Invalid Token. {identifier.value} should be followed by RPAR token `)`. {self.tokens.line}"
                    )
                self.tokens.selectNext()
                if self.tokens.actual.tokenType != TokenTypes.SEPARATOR:
                    raise BufferError(
                        "Invalid Token. Line should end with separator `;`"
                    )
                return Print(identifier, value)
            elif identifier.value == "while":
                logger.logParse(f"[INFO] [COMMAND] While")
                if self.tokens.actual.tokenType != TokenTypes.LPAR:
                    raise BufferError(
                        f"Invalid Token. {identifier.value} should be followed by LPAR token `(`"
                    )
                condition = self.parseOrExpr()
                logger.logParse(f"[INFO] [COMMAND] While Condition {condition}")
                # self.tokens.selectNext()
                if self.tokens.actual.tokenType != TokenTypes.RPAR:
                    raise BufferError(
                        f"Invalid Token. {identifier.value} should be followed by RPAR token `)` {self.tokens.line}"
                    )
                self.tokens.selectNext()
                command = self.parseCommand()
                logger.logParse(f"[INFO] [COMMAND] While Condition {command}")
                return While(identifier, condition, command)
            elif identifier.value == "if":
                logger.logParse(f"[INFO] [COMMAND] If")
                if self.tokens.actual.tokenType != TokenTypes.LPAR:
                    raise BufferError(
                        f"Invalid Token. {identifier.value} should be followed by LPAR token `(`"
                    )
                condition = self.parseOrExpr()
                logger.logParse(f"[INFO] [COMMAND] If Condition {condition}")
                # self.tokens.selectNext()
                # print(self.tokens.actual.tokenType)
                # print(self.tokens.actual.tokenType)
                if self.tokens.actual.tokenType != TokenTypes.RPAR:
                    raise BufferError(
                        f"Invalid Token. {identifier.value} should be followed by RPAR token `)` {self.tokens.actual.tokenType}"
                    )
                self.tokens.selectNext()
                command = self.parseCommand()
                logger.logParse(f"[INFO] [COMMAND] If command {command}")
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
                logger.logParse(f"[INFO] [COMMAND] Else command {command}")
                command.value = identifier
                return command
            elif identifier.value == "return":
                self.tokens.position -= len(self.tokens.actual.value)
                command = self.parseOrExpr()
                logger.logParse(f"[INFO] [COMMAND] Return command {command}")
                return Return(identifier, command)
            else:
                logger.logParse(f"[INFO] [COMMAND] Identifier")
                if self.tokens.actual.tokenType != TokenTypes.ASSIGN:
                    if self.tokens.actual.tokenType == TokenTypes.LPAR:
                        func = FuncCall(identifier)
                        logger.logParse(f"[INFO] [COMMAND] Funccall {identifier.value}")
                        while self.tokens.actual.tokenType != TokenTypes.RPAR:
                            logger.logParse(f"[INFO] [COMMAND] Adding param")
                            func.addArgument(self.parseOrExpr())
                        self.tokens.selectNext()
                        if self.tokens.actual.tokenType != TokenTypes.SEPARATOR:
                            raise BufferError(
                                "Invalid Token. Line should end with separator `;`"
                            )
                        return func
                    raise BufferError(
                        "Invalid Token. Identifier should be followed by assigner token `=`"
                    )
                root = Assigner(identifier, self.parseOrExpr())
                logger.logParse(f"[INFO] [COMMAND] Assignment {root}")
                if self.tokens.actual.tokenType != TokenTypes.SEPARATOR:
                    raise BufferError(
                        f"Invalid Token. Line should end with separator `;`. Line {self.tokens.line}. Token {self.tokens.actual.value}"
                    )
                return root
        elif self.tokens.actual.tokenType == TokenTypes.SEPARATOR:
            logger.logParse(f"[INFO] [COMMAND] Empty Line")
            self.tokens.selectNext()
            return NoOp(self.tokens.actual)
        elif self.tokens.actual.tokenType == TokenTypes.BLOCK_OPENER:
            logger.logParse(f"[INFO] [COMMAND] Block Found")
            return self.parseBlock()
        raise BufferError(f"Invalid line {self.tokens.line}")

    def parseOrExpr(self) -> Node:
        node = self.parseAndExpr()
        root = BinOp(Token(TokenTypes.EOF, 0), node, NoOp(Token(TokenTypes.EOF, 0)))
        logger.logParse(f"[DEBUG] [OREXPR] [PREWHILE] {self.tokens.actual.value}")
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
        logger.logParse(f"[DEBUG] [ANDEXPR] [PREWHILE] {self.tokens.actual.value}")
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
        logger.logParse(f"[DEBUG] [EQEXPR] [PREWHILE] {self.tokens.actual.value}")
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
        logger.logParse(f"[DEBUG] [RELEXPR] [PREWHILE] {self.tokens.actual.value}")
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
        logger.logParse(f"[DEBUG] [EXPR] [PREWHILE] {self.tokens.actual.value}")
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
        logger.logParse(f"[DEBUG] [TERM] [PRESELECTNEXT] {self.tokens.actual.value}")
        self.tokens.selectNext()
        logger.logParse(
            f"[DEBUG] [TERM] [PREWHILE] {self.tokens.actual.value} {self.tokens.actual.tokenType}"
        )
        while self.tokens.actual.tokenType in self.levelOneTokens:
            root.setValue(self.tokens.actual)
            root.setRight(self.parseFactor())
            tmp = BinOp(Token(TokenTypes.EOF, 0), root, NoOp(Token(TokenTypes.EOF, 0)))
            root = tmp
            self.tokens.selectNext()
        root = root.children[0]
        return root

    def parseFactor(self) -> Node:
        logger.logParse(f"[DEBUG] [INFACTOR] [PRESELECT] {self.tokens.actual.value}")
        self.tokens.selectNext()
        logger.logParse(f"[DEBUG] [INFACTOR] [POSSELECT] {self.tokens.actual.value}")
        if self.tokens.actual.tokenType == TokenTypes.NUMBER:
            logger.logParse(f"[INFO] [FACTOR] Number found {self.tokens.actual.value}")
            return IntVal(self.tokens.actual)
        elif (
            self.tokens.actual.tokenType in self.levelZeroTokens
            or self.tokens.actual.tokenType == TokenTypes.BOOL_NOT
        ):
            logger.logParse(
                f"[INFO] [FACTOR] Unop Found {self.tokens.actual.tokenType}"
            )
            return UnOp(self.tokens.actual, self.parseFactor())
        elif self.tokens.actual.tokenType == TokenTypes.RPAR:
            raise ValueError()
        elif self.tokens.actual.tokenType == TokenTypes.IDENTIFIER:
            logger.logParse(
                f"[INFO] [FACTOR] Identifier found {self.tokens.actual.value}"
            )
            if self.tokens.actual.value != "readln":
                identifier = self.tokens.actual
                self.tokens.selectNext()
                if self.tokens.actual.tokenType == TokenTypes.LPAR:
                    func = FuncCall(identifier)
                    logger.logParse(f"[INFO] [FACTOR] Funccall")
                    while self.tokens.actual.tokenType != TokenTypes.RPAR:
                        logger.logParse(f"[INFO] [FACTOR] Add param to func")
                        func.addArgument(self.parseOrExpr())
                    return func
                else:
                    logger.logParse(
                        f"[DEBUG] [FACTOR] Identifier Len {len(self.tokens.actual.value)}"
                    )
                    self.tokens.position -= len(self.tokens.actual.value)
                    self.tokens.actual = identifier
                    return IdentifierVal(Token(TokenTypes.IDENTIFIER, identifier.value))
            self.tokens.selectNext()
            if self.tokens.actual.tokenType != TokenTypes.LPAR:
                raise BufferError()
            self.tokens.selectNext()
            if self.tokens.actual.tokenType != TokenTypes.RPAR:
                raise BufferError()
            return Readln(self.tokens.actual)
        elif self.tokens.actual.tokenType == TokenTypes.LPAR:
            logger.logParse(f"[INFO] [FACTOR] LPAREN")
            self.openPars += 1
            logger.logParse(
                f"[DEBUG] [IN-FACTOR] In LPAR {self.openPars} {self.tokens.actual.value}"
            )
            root = self.parseOrExpr()
            logger.logParse(f"[INFO] [FACTOR] Factor {root}")
            if self.tokens.actual.tokenType == TokenTypes.RPAR:
                logger.logParse(f"[INFO] [FACTOR] RPAREN")
                self.openPars -= 1
        elif self.tokens.actual.tokenType == TokenTypes.STRING:
            logger.logParse(f"[INFO] [FACTOR] String found {self.tokens.actual.value}")
            return StrVal(self.tokens.actual)
        elif self.tokens.actual.tokenType == TokenTypes.BOOLEAN:
            logger.logParse(f"[INFO] [FACTOR] Bool found {self.tokens.actual.value}")
            return BoolVal(self.tokens.actual)
        else:
            raise BufferError(
                f"Invalid token type on factor. {self.tokens.actual.tokenType}"
            )
        return root

    def run(self) -> NoReturn:
        self.tokens.selectNext()
        block = self.parseFuncDefBlock()
        self.tokens.selectNext()
        if (
            self.openPars == 0
            and self.openBlocks == 0
            and self.tokens.actual.tokenType == TokenTypes.EOF
        ):
            block.addNode(FuncCall(Token(TokenTypes.IDENTIFIER, "main")))
            block.evaluate(self.symbols)
        else:
            raise BufferError(
                f"Open Pars: {self.openPars} | Open Blocks: {self.openBlocks} | Last Token: {self.tokens.actual.tokenType}"
            )


if __name__ == "__main__":
    f = sys.argv[1]
    # f = "test1.c"
    with open(f, "r") as tmp:
        sentence = tmp.read()
    logger = Logger("./out/debug.log")
    parser = Parser(sentence, logger)
    parser.run()
