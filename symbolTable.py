from typing import NoReturn, Dict, Union
from tokens import Token
from logger import Logger

LOGGER = Logger("./out/debug.log")


class SymbolTable:

    table: Dict[str, Token]

    def __init__(self):
        self.table = {}

    def getVariable(self, variable: str):
        if variable in self.table:
            LOGGER.logParse(f"[DEBUG] [SYMBOLTABLE] [GET] Getting {variable}. {self}")
            return self.table[variable]["value"], self.table[variable]["varType"]
        raise KeyError(f"No variable named {variable}")

    def declareVariable(
        self, variable: str, value: Union[int, str, bool], varType: str
    ) -> NoReturn:
        if variable in self.table:
            raise NameError(f"Variable {variable} already declared")
        LOGGER.logParse(
            f"[DEBUG] [SYMBOLTABLE] [DECLARE] Declaring {variable} of type {varType} to scope. {self}"
        )
        self.table[variable] = {"value": value, "varType": varType}

    def setVariable(
        self, variable: str, value: Union[int, str, bool], varType: str
    ) -> NoReturn:
        if variable not in self.table:
            raise NameError(f"Variable {variable} not declared")
        elif varType != self.table[variable]["varType"]:
            if varType == "int" and self.table[variable]["varType"] == "bool":
                value = bool(value)
            elif varType == "bool" and self.table[variable]["varType"] == "int":
                value = int(value)
            else:
                raise TypeError()
        LOGGER.logParse(
            f"[DEBUG] [SYMBOLTABLE] [SET] Setting {variable} of value {value} to scope. {self}"
        )
        self.table[variable]["value"] = value
