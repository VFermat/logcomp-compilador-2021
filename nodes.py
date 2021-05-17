from typing import List, NoReturn, Union
from tokens import Token, TokenTypes
from symbolTable import SymbolTable


VARTYPES = Union[str, bool, int]

class Node:
    def __init__(self, value: Token):
        self.value = value
        self.children = []

    def evaluate(self, table: SymbolTable) -> int:
        return 0


class Block(Node):

    child: List[Node]

    def __init__(self, value: Token):
        self.value = value
        self.child = []

    def evaluate(self, table: SymbolTable):
        for node in self.child:
            node.evaluate(table)

    def addNode(self, node: Node):
        self.child.append(node)


class Assigner(Node):

    child: Node

    def __init__(self, value: Token, child: Node, varType: str = None):
        self.value = value
        self.child = child
        self.varType = varType

    def evaluate(self, table: SymbolTable) -> SymbolTable:
        value = self.child.evaluate(table)
        if self.varType:
            table.declareVariable(self.value.value, value[0], self.varType)
        else:
            table.setVariable(self.value.value, value[0], value[1])
        return table


class Print(Node):

    child: Node

    def __init__(self, value: Token, child: Node):
        super().__init__(value)
        self.child = child

    def evaluate(self, table: SymbolTable):
        print(self.child.evaluate(table)[0])


class While(Node):

    condition: Node
    command: Node

    def __init__(self, value, condition: Node, command: Node):
        super().__init__(value)
        self.condition = condition
        self.command = command

    def evaluate(self, table):
        while self.condition.evaluate(table)[0]:
            self.command.evaluate(table)


class If(Node):

    condition: Node
    commandTrue: Node
    commandFalse: Node

    def __init__(self, value: Token, condition: Node, commandTrue: Node):
        super().__init__(value)
        self.condition = condition
        self.commandTrue = commandTrue
        self.commandFalse = None

    def setCommandFalse(self, commandFalse: Node) -> NoReturn:
        self.commandFalse = commandFalse

    def evaluate(self, table):
        if self.condition.evaluate(table)[0]:
            return self.commandTrue.evaluate(table)
        elif self.commandFalse is not None:
            return self.commandFalse.evaluate(table)


class Readln(Node):
    def __init__(self, value):
        super().__init__(value)

    def evaluate(self, table) -> Token:
        value = input()
        if value.isnumeric():
            return Token(TokenTypes.NUMBER, int(value), 'int')
        else:
            return Token(TokenTypes.IDENTIFIER, value, 'str')


class BinOp(Node):

    children: List[Node]

    def __init__(self, value: Token, left: Node, right: Node):
        super().__init__(value)
        self.children = [left, right]

    def evaluate(self, table: SymbolTable):
        childrenZero = self.children[0].evaluate(table)
        childrenOne = self.children[1].evaluate(table)
        if self.value.tokenType == TokenTypes.PLUS:
            return int(childrenZero[0]) + int(childrenOne[0]), 'int'
        elif self.value.tokenType == TokenTypes.MINUS:
            return int(childrenZero[0]) - int(childrenOne[0]), 'int'
        elif self.value.tokenType == TokenTypes.MULTIPLIER:
            return int(childrenZero[0]) * int(childrenOne[0]), 'int'
        elif self.value.tokenType == TokenTypes.DIVIDER:
            return int(childrenZero[0]) / int(childrenOne[0]), 'int'
        elif self.value.tokenType == TokenTypes.BOOL_AND:
            return bool(childrenZero[0] and childrenOne[0]), 'bool'
        elif self.value.tokenType == TokenTypes.BOOL_OR:
            return bool(childrenZero[0] or childrenOne[0]), 'bool'
        elif self.value.tokenType == TokenTypes.BOOL_GT:
            return bool(childrenZero[0] > childrenOne[0]), 'bool'
        elif self.value.tokenType == TokenTypes.BOOL_LT:
            return bool(childrenZero[0] < childrenOne[0]), 'bool'
        elif self.value.tokenType == TokenTypes.BOOL_EQUAL:
            return bool(childrenZero[0] == childrenOne[0]), 'bool'
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
        self.child = child

    def evaluate(self, table: SymbolTable):
        child = self.child.evaluate(table)
        if self.value.tokenType == TokenTypes.PLUS:
            return +child[0], child[1]
        elif self.value.tokenType == TokenTypes.MINUS:
            return -child[0], child[1]
        elif self.value.tokenType == TokenTypes.BOOL_NOT:
            return not child[0], child[1]
        else:
            raise BufferError()


class IdentifierVal(Node):
    def __init__(self, value: Token):
        super().__init__(value)

    def evaluate(self, table: SymbolTable):
        return table.getVariable(self.value.value)


class IntVal(Node):

    def __init__(self, value: Token):
        super().__init__(value)

    def evaluate(self, table: SymbolTable):
        return self.value.value, 'int'


class BoolVal(Node):

    def __init__(self, value: Token):
        super().__init__(value)

    def evaluate(self, table: SymbolTable):
        return bool(self.value.value), 'bool'

class StrVal(Node):

    def __init__(self, value: Token):
        super().__init__(value)

    def evaluate(self, table: SymbolTable):
        return self.value.value, 'str'


class NoOp(Node):

    def __init__(self, value: Token):
        super().__init__(value)

    def evaluate(self, table: SymbolTable):
        return 0, 'int'
