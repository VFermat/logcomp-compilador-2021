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

class Token:

    tokenType: TokenTypes
    value: int

    def __init__(self, tokenType: TokenTypes, value: int):
        self.tokenType = tokenType
        self.value = value