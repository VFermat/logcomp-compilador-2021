import sys
from typing import List
from enum import Enum

class TokenTypes(Enum):
    NUMBER = 1
    EOF = 2
    PLUS = 3
    MINUS = 4

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
                continue
            else:
                exit(1)
            i += 1
        self.actual = token
        self.position = i+1
        return token

class Parser:

    tokens: Tokenizer

    def __init__(self, code: str):
        self.tokens = Tokenizer(code)

    def main(self):
        return self.__parseExpression(self.__run(self.tokens))

    @staticmethod
    def __parseExpression(tokens: List[Token]) -> int:
        total = 0
        i = 0
        actual = tokens[i]
        while i < len(tokens) - 1:
            nextToken = tokens[i+1]
            if nextToken.tokenType == actual.tokenType or (actual.tokenType in [TokenTypes.PLUS, TokenTypes.MINUS] and nextToken.tokenType in [TokenTypes.PLUS, TokenTypes.MINUS]):
                raise BufferError()
            elif actual.tokenType == TokenTypes.PLUS:
                total += nextToken.value
            elif actual.tokenType == TokenTypes.MINUS:
                total -= nextToken.value
            elif actual.tokenType == TokenTypes.NUMBER and i == 0:
                total += actual.value
            actual = nextToken
            i += 1
        if tokens[-1].tokenType != TokenTypes.EOF:
            raise EOFError()
        return total

    @staticmethod
    def __run(tokens: Tokenizer):
        validTokens = []
        validTokens.append(tokens.selectNext())
        while tokens.actual.tokenType != TokenTypes.EOF:
            validTokens.append(tokens.selectNext())
        return validTokens


sentence = sys.argv[1].strip()
parser = Parser(sentence)
print(parser.main())
