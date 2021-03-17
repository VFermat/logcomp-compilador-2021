import sys
from typing import List
from enum import Enum

class TokenTypes(Enum):
    NUMBER = 1
    EOF = 2
    PLUS = 3
    MINUS = 4
    MULTIPLIER = 5
    DIVIDER = 6
    LPAR = 7
    RPAR = 8

class PrePro:

    def filter(self, text: str) -> str:
        text = text.strip()
        position: int = text.find("/*")
        while position != -1:
            end_position: int = text[position:].find("*/")
            if end_position:
                text = text[:position] + text[position+end_position+2:]
            else:
                raise ValueError()
            position = text.find("/*")
        return text.strip()

class Token:

    tokenType: TokenTypes
    value: int

    def __init__(self, tokenType: TokenTypes, value: int):
        self.tokenType = tokenType
        self.value = value

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

    def parseExpression(self) -> int:
        total = self.parseTerm()
        while self.tokens.actual.tokenType in self.levelZeroTokens:
            if self.tokens.actual.tokenType == TokenTypes.MINUS:
                total -= self.parseTerm()
            elif self.tokens.actual.tokenType == TokenTypes.PLUS:
                total += self.parseTerm()
        return total

    def parseTerm(self) -> int:
        total = self.parseFactor()
        self.tokens.selectNext()
        while self.tokens.actual.tokenType in self.levelOneTokens:
            if self.tokens.actual.tokenType == TokenTypes.DIVIDER:
                self.tokens.selectNext()
                if self.tokens.actual.tokenType == TokenTypes.NUMBER:
                    total = int(total // self.tokens.actual.value)
                elif self.tokens.actual.tokenType in self.levelOneTokens:
                    raise BufferError("Dupla operação com Divisor")
                self.tokens.selectNext()
            elif self.tokens.actual.tokenType == TokenTypes.MULTIPLIER:
                self.tokens.selectNext()
                if self.tokens.actual.tokenType == TokenTypes.NUMBER:
                    total *= self.tokens.actual.value
                elif self.tokens.actual.tokenType in self.levelOneTokens:
                    raise BufferError("Dupla operação com multiplicador")
                self.tokens.selectNext()
        return total
    
    def parseFactor(self) -> int:
        self.tokens.selectNext()
        total = 0
        if self.tokens.actual.tokenType == TokenTypes.NUMBER:
            total = self.tokens.actual.value
        elif self.tokens.actual.tokenType == TokenTypes.MINUS:
            total -= self.parseFactor()
        elif self.tokens.actual.tokenType == TokenTypes.PLUS:
            total += self.parseFactor()
        elif self.tokens.actual.tokenType == TokenTypes.RPAR:
            self.openPars -= 1
            total = 0
        elif self.tokens.actual.tokenType == TokenTypes.LPAR:
            self.openPars += 1
            total = self.parseExpression()
        else:
            raise BufferError(f"Invalid token type on factor. {self.tokens.actual.tokenType}")
        return total

    def run(self):
        total = self.parseExpression()
        if self.openPars != 0:
            raise BufferError("Parenteses fechados não correspondem aos abertos")
        if self.tokens.actual.tokenType != TokenTypes.EOF:
            raise EOFError("Missing EOF")
        return total

if __name__ == "__main__":
    # sentence = sys.argv[1]
    sentence = "3 - -2/4"
    parser = Parser(sentence)
    print(parser.run())

