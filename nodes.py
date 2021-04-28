from typing import List, NoReturn
from tokens import Token, TokenTypes
from symbolTable import SymbolTable

class Node:

    def __init__(self, value: Token):
        self.value = value
        self.children = []

    def evaluate(self, table: SymbolTable) -> int:
        return 0

class Block(Node):

    child: List[Node]

    def __init__(self):
        self.child = []

    def evaluate(self, table: SymbolTable):
        for node in self.child:
            node.evaluate(table)

    def addNode(self, node: Node):
        self.child.append(node)

class Assigner(Node):

    child: Node

    def __init__(self, value: Token, child: Node):
        self.value = value
        self.child = child

    def evaluate(self, table: SymbolTable) -> SymbolTable:
        table.setVariable(self.value.value, self.child.evaluate(table))
        return table

class Print(Node):

    child: Node

    def __init__(self, value: Token, child: Node):
        super().__init__(value)
        self.child = child

    def evaluate(self, table: SymbolTable):
        print(self.child.evaluate(table))

class BinOp(Node):

    children: List[Node]

    def __init__(self, value: Token, left: Node, right: Node):
        super().__init__(value)
        self.children = [left, right]
    
    def evaluate(self, table: SymbolTable) -> int:
        if self.value.tokenType == TokenTypes.PLUS:
            return self.children[0].evaluate(table) + self.children[1].evaluate(table)
        elif self.value.tokenType == TokenTypes.MINUS:
            return self.children[0].evaluate(table) - self.children[1].evaluate(table)
        elif self.value.tokenType == TokenTypes.MULTIPLIER:
            return self.children[0].evaluate(table) * self.children[1].evaluate(table)
        elif self.value.tokenType == TokenTypes.DIVIDER:
            return self.children[0].evaluate(table) // self.children[1].evaluate(table)
        else:
            raise BufferError()

    def setValue(self, value: Token) -> NoReturn:
        self.value = value

    def setLeft(self, left: Node) -> NoReturn:
        self.children[0] = left

    def setRight(self, right: Node) -> NoReturn:
        self.children[1] = right
    
class UnOp(Node):

    child: Node

    def __init__(self, value: Token, child: Node):
        super().__init__(value)
        self.children = child

    def evaluate(self, table: SymbolTable) -> int:
        if self.value.tokenType == TokenTypes.PLUS:
            return +self.children.evaluate(table)
        elif self.value.tokenType == TokenTypes.MINUS:
            return -self.children.evaluate(table)
        else:
            raise BufferError()

class IdentifierVal(Node):

    def __init__(self, value: Token):
        super().__init__(value)

    def evaluate(self, table: SymbolTable) -> int:
        return table.getVariable(self.value.value)

class IntVal(Node):

    child: Node

    def __init__(self, value: Token):
        super().__init__(value)

    def evaluate(self, table: SymbolTable) -> int:
        return self.value.value

class NoOp(Node):

    children: List[Node]

    def __init__(self, value: Token):
        super().__init__(value)

    def evaluate(self, table: SymbolTable) -> int:
        return 0
