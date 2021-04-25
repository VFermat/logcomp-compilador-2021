import sys
from typing import List, NoReturn
from enum import Enum
from tokens import Token, TokenTypes
from nodes import BinOp, UnOp, IntVal, NoOp, Node
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


class Tokenizer:

    position: str
    position: int
    actual: Token

    def __init__(self, origin: str):
        self.origin = origin
        self.position = 0
        self.actual = None

    def selectNext(self) -> Token:
        if self.position == len(self.origin):
            token = Token(TokenTypes.EOF, 0)
            self.actual = token
            return token
        i = self.position
        while i < len(self.origin):
            char = self.origin[i]
            if char == "+":
                token = Token(TokenTypes.PLUS, 1)
                break
            elif char == "-":
                token = Token(TokenTypes.MINUS, 1)
                break
            elif char == "/":
                token = Token(TokenTypes.DIVIDER, 1)
                break
            elif char == "*":
                token = Token(TokenTypes.MULTIPLIER, 1)
                break
            elif char == "=":
                token = Token(TokenTypes.ASSIGN, 0)
                break
            elif char == ";":
                token = Token(TokenTypes.SEPARATOR, 0)
                break
            elif char.isdigit():
                temp = char
                if i < len(self.origin) - 1:
                    while self.origin[i + 1].isdigit():
                        char = self.origin[i + 1]
                        i += 1
                        temp += char
                        if i == len(self.origin) - 1:
                            break
                token = Token(TokenTypes.NUMBER, int(temp))
                break
            elif char == "(":
                token = Token(TokenTypes.LPAR, 1)
                break
            elif char == ")":
                token = Token(TokenTypes.RPAR, 1)
                break
            elif char == " ":
                i += 1
            elif char.isalpha():
                temp = char
                if i < len(self.origin) - 1:
                    while self.origin[i + 1].isalpha():
                        char = self.origin[i + 1]
                        i += 1
                        temp += char
                        if i == len(self.origin) - 1:
                            break
                token = Token(TokenTypes.IDENTIFIER, temp)
                break
            else:
                raise ValueError()
        self.actual = token
        self.position = i + 1
        return token


class Parser:

    tokens: Tokenizer
    levelZeroTokens: List[TokenTypes] = [TokenTypes.PLUS, TokenTypes.MINUS]
    levelOneTokens: List[TokenTypes] = [TokenTypes.MULTIPLIER, TokenTypes.DIVIDER]
    reservedWords: List[str] = ["println"]
    openPars: int = 0
    symbols: SymbolTable

    def __init__(self, code: str):
        prepro = PrePro()
        code = prepro.filter(code)
        self.tokens = Tokenizer(code)
        self.symbols = SymbolTable()

    def parseBlock(self) -> NoReturn:
        self.tokens.selectNext()
        while self.tokens.actual.tokenType != TokenTypes.EOF:
            self.parseCommand()
            self.tokens.selectNext()

    def parseCommand(self) -> NoReturn:
        if self.tokens.actual.tokenType == TokenTypes.IDENTIFIER:
            identifier = self.tokens.actual.value
            if identifier == 'println':
                self.tokens.selectNext()
                if self.tokens.actual.tokenType != TokenTypes.LPAR:
                    raise BufferError(
                        "Invalid Token. Print should be followed by LPAR token `(`"
                    )
                value = self.parseExpression()
                if self.tokens.actual.tokenType != TokenTypes.RPAR:
                    raise BufferError(
                        "Invalid Token. Print expression should be followed by RPAR token `)`"
                    )
                self.tokens.selectNext()
                if self.tokens.actual.tokenType != TokenTypes.SEPARATOR:
                    raise BufferError("Invalid Token. Line should end with separator `;`")
                print(value.evaluate())
            else:
                self.tokens.selectNext()
                if self.tokens.actual.tokenType != TokenTypes.ASSIGN:
                    raise BufferError(
                        "Invalid Token. Identifier should be followed by assigner token `=`"
                    )
                self.symbols.setVariable(identifier, self.parseExpression())
                if self.tokens.actual.tokenType != TokenTypes.SEPARATOR:
                    raise BufferError("Invalid Token. Line should end with separator `;`")
        
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
        elif self.tokens.actual.tokenType in self.levelZeroTokens:
            return UnOp(self.tokens.actual, self.parseFactor())
        elif self.tokens.actual.tokenType == TokenTypes.RPAR:
            raise ValueError()
        elif self.tokens.actual.tokenType == TokenTypes.IDENTIFIER:
            root = self.symbols.getVariable(self.tokens.actual.value)
        elif self.tokens.actual.tokenType == TokenTypes.LPAR:
            self.openPars += 1
            root = self.parseExpression()
            if self.tokens.actual.tokenType == TokenTypes.RPAR:
                self.openPars -= 1
        else:
            raise BufferError(
                f"Invalid token type on factor. {self.tokens.actual.tokenType}"
            )
        return root

    def run(self):
        self.parseBlock()


if __name__ == "__main__":
    # f = sys.argv[1]
    f = "test.c"
    with open(f, "r") as tmp:
        sentence = tmp.read()
    parser = Parser(sentence)
    parser.run()
