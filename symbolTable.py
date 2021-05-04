from typing import NoReturn, Dict


class SymbolTable:

    table: Dict[str, int]

    def __init__(self):
        self.table = {}

    def getVariable(self, variable: str):
        if variable in self.table:
            return self.table[variable]
        raise KeyError(f"No variable named {variable}")

    def setVariable(self, variable: str, value: int) -> NoReturn:
        self.table[variable] = value