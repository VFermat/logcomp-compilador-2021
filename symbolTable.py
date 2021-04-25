from typing import NoReturn, Dict
from nodes import Node

class SymbolTable():

    table: Dict[str, Node]

    def __init__(self):
        self.table = {}
    
    def getVariable(self, variable: str):
        if variable in self.table:
            return self.table[variable]
        raise KeyError(f"No variable named {variable}")

    def setVariable(self, variable: str, value: Node) -> NoReturn:
        self.table[variable] = value