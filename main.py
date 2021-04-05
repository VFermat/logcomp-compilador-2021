import sys
from typing import List
from enum import Enum
from tokens import Token, TokenTypes
from nodes import BinOp, UnOp, IntVal, NoOp, Node

class PrePro:

    def filter(self, text: str) -> str:
        text = text.strip()
        position: int = text.find("/*")
        while position != -1:
            end_position: int = text[position:].find("*/")
            if end_position != -1:
                text = text[:position] + text[position+end_position+2:]
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
            if char == '+':
                token = Token(TokenTypes.PLUS, 1)
                break
            elif char == '-':
                token = Token(TokenTypes.MINUS, 1)
                break
            elif char == '/':
                token = Token(TokenTypes.DIVIDER, 1)
                break
            elif char == '*':
                token = Token(TokenTypes.MULTIPLIER, 1)
                break
            elif char.isdigit():
                temp = char
                if i < len(self.origin) - 1:
                    while self.origin[i+1].isdigit():
                        char = self.origin[i+1]
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
            else:
                raise ValueError()
        self.actual = token
        self.position = i+1
        return token

class Parser:
    
    tokens: Tokenizer
    levelZeroTokens = [TokenTypes.PLUS, TokenTypes.MINUS]
    levelOneTokens = [TokenTypes.MULTIPLIER, TokenTypes.DIVIDER]
    openPars: int = 0

    def __init__(self, code: str):
        prepro = PrePro()
        code = prepro.filter(code)
        self.tokens = Tokenizer(code)

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
        elif self.tokens.actual.tokenType == TokenTypes.LPAR:
            self.openPars += 1
            root = self.parseExpression()
            if self.tokens.actual.tokenType == TokenTypes.RPAR:
                self.openPars -= 1
        else:
            raise BufferError(f"Invalid token type on factor. {self.tokens.actual.tokenType}")
        return root

    def run(self):
        root = self.parseExpression()
        if self.openPars != 0:
            raise BufferError("Parenteses fechados não correspondem aos abertos")
        if self.tokens.actual.tokenType != TokenTypes.EOF:
            raise EOFError()
        return root.evaluate()

if __name__ == "__main__":
    f = sys.argv[1]
    # f = "test.c"
    with open(f, 'r') as tmp:
        sentence = tmp.read()
    parser = Parser(sentence)
    print(parser.run())

