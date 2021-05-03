from typing import List, Union
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
    IDENTIFIER = 9
    ASSIGN = 10
    SEPARATOR = 11
    PRINT = 12
    BLOCK_OPENER = 13
    BLOCK_CLOSER = 14
    BOOL_EQUAL = 15
    BOOL_AND = 16
    BOOL_OR = 17
    BOOL_GT = 18
    BOOL_LT = 19
    BOOL_NOT = 20

class Token:

    tokenType: TokenTypes
    value: Union[int, str]

    def __init__(self, tokenType: TokenTypes, value: int):
        self.tokenType = tokenType
        self.value = value
