from typing import NoReturn, Dict, Union
from tokens import Token


class SymbolTable:

    table: Dict[str, Token]
    variableId: int

    def __init__(self):
        self.table = {}
        self.variableId = 1

    def getVariable(self, variable: str) -> Token:
        if variable in self.table:
            return self.table[variable]["value"], self.table[variable]["varType"], self.table[variable]["variableId"]
        raise KeyError(f"No variable named {variable}")

    def declareVariable(
        self, variable: str, value: Union[int, str, bool], varType: str
    ) -> int:
        if variable in self.table:
            raise NameError(f"Variable {variable} already declared")
        self.table[variable] = {"value": value, "varType": varType, "variableId": self.variableId}
        self.variableId += 1
        return self.table[variable]["variableId"]

    def setVariable(
        self, variable: str, value: Union[int, str, bool], varType: str
    ) -> int:
        if variable not in self.table:
            raise NameError(f"Variable {variable} not declared")
        elif varType != self.table[variable]["varType"]:
            if varType == 'int' and self.table[variable]["varType"] == 'bool':
                value = bool(value)
            elif varType == 'bool' and self.table[variable]["varType"] == 'int':
                value = int(value)
            else:
                raise TypeError()
        self.table[variable]["value"] = value
        return self.table[variable]["variableId"]

