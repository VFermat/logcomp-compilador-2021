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
    COMMENT = 7

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

    def __init__(self, code: str):
        self.tokens = Tokenizer(code)

    def main(self):
        return self.parseExpression()

    def parseExpression(self) -> int:
        total = self.parseMultDiv()
        actual = self.tokens.actual
        while actual.tokenType in self.levelZeroTokens:
            if actual.tokenType == TokenTypes.MINUS:
                total -= self.parseMultDiv()
            elif actual.tokenType == TokenTypes.PLUS:
                total += self.parseMultDiv()
            actual = self.tokens.actual
        return total
    
    def parseMultDiv(self) -> int:
        actual = self.tokens.selectNext()
        if actual.tokenType != TokenTypes.NUMBER:
            raise BufferError()
        total = actual.value
        actual = self.tokens.selectNext()
        while actual.tokenType in self.levelOneTokens:
            if actual.tokenType == TokenTypes.DIVIDER:
                actual = self.tokens.selectNext()
                if actual.tokenType == TokenTypes.NUMBER:
                    total /= actual.value
                actual = self.tokens.selectNext()
            elif actual.tokenType == TokenTypes.MULTIPLIER:
                actual = self.tokens.selectNext()
                if actual.tokenType == TokenTypes.NUMBER:
                    total *= actual.value
                actual = self.tokens.selectNext()
        return total

    @staticmethod
    def __run(tokens: Tokenizer):
        validTokens = []
        validTokens.append(tokens.selectNext())
        while tokens.actual.tokenType != TokenTypes.EOF:
            validTokens.append(tokens.selectNext())
        return validTokens

if __name__ == "__main__":
    sentence = sys.argv[1].strip()
    parser = Parser(sentence)
    # parser = Parser('4+3*5')
    print(parser.main())

