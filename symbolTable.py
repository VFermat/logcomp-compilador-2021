from typing import NoReturn

class SymbolTable():

    def __init__(self):
        self.table = {}
    
    def getVariable(self, variable: str):
        if variable in self.table:
            return self.table[variable]
        raise KeyError(f"No variable named {variable}")

    def setVariable(self, variable: str, value) -> NoReturn:
        self.table[variable] = value