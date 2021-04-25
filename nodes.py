from typing import List, NoReturn
from tokens import Token, TokenTypes

class Node:

    def __init__(self, value: Token):
        self.value = value
        self.children = []

    def evaluate(self) -> int:
        return 0

class Print(Node):

    child: Node

    def __init__(self, value: Token, child: Node):
        super().__init__(value)
        self.child = child

    def evaluate(self):
        print(self.child.evaluate())

class BinOp(Node):

    children: List[Node]

    def __init__(self, value: Token, left: Node, right: Node):
        super().__init__(value)
        self.children = [left, right]
    
    def evaluate(self) -> int:
        if self.value.tokenType == TokenTypes.PLUS:
            return self.children[0].evaluate() + self.children[1].evaluate()
        elif self.value.tokenType == TokenTypes.MINUS:
            return self.children[0].evaluate() - self.children[1].evaluate()
        elif self.value.tokenType == TokenTypes.MULTIPLIER:
            return self.children[0].evaluate() * self.children[1].evaluate()
        elif self.value.tokenType == TokenTypes.DIVIDER:
            return self.children[0].evaluate() // self.children[1].evaluate()
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

    def evaluate(self) -> int:
        if self.value.tokenType == TokenTypes.PLUS:
            return +self.children.evaluate()
        elif self.value.tokenType == TokenTypes.MINUS:
            return -self.children.evaluate()
        else:
            raise BufferError()

class IntVal(Node):

    child: Node

    def __init__(self, value: Token):
        super().__init__(value)

    def evaluate(self) -> int:
        return self.value.value

class NoOp(Node):

    children: List[Node]

    def __init__(self, value: Token):
        super().__init__(value)

    def evaluate(self) -> int:
        return 0
