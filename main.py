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
        prepro = PrePro()
        code = prepro.filter(code)
        self.tokens = Tokenizer(code)

    def main(self):
        return self.parseExpression()

    def parseExpression(self) -> int:
        total = self.parseMultDiv()
        while self.tokens.actual.tokenType in self.levelZeroTokens:
            if self.tokens.actual.tokenType == TokenTypes.MINUS:
                total -= self.parseMultDiv()
            elif self.tokens.actual.tokenType == TokenTypes.PLUS:
                total += self.parseMultDiv()
        return total
    
    def parseMultDiv(self) -> int:
        self.tokens.selectNext()
        if self.tokens.actual.tokenType != TokenTypes.NUMBER:
            raise BufferError()
        total = self.tokens.actual.value
        self.tokens.selectNext()
        while self.tokens.actual.tokenType in self.levelOneTokens:
            if self.tokens.actual.tokenType == TokenTypes.DIVIDER:
                self.tokens.selectNext()
                if self.tokens.actual.tokenType == TokenTypes.NUMBER:
                    total /= self.tokens.actual.value
                self.tokens.selectNext()
            elif self.tokens.actual.tokenType == TokenTypes.MULTIPLIER:
                self.tokens.selectNext()
                if self.tokens.actual.tokenType == TokenTypes.NUMBER:
                    total *= self.tokens.actual.value
                self.tokens.selectNext()
        return total

    @staticmethod
    def __run(tokens: Tokenizer):
        raise NotImplementedError

if __name__ == "__main__":
    sentence = sys.argv[1]
    # sentence = "/* a */ 1 /* b */"
    parser = Parser(sentence)
    # parser = Parser('4+3*5')
    print(parser.main())

