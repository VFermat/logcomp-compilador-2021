from typing import List, NoReturn, Union
from tokens import Token, TokenTypes
from symbolTable import SymbolTable
from logger import Logger


VARTYPES = Union[str, bool, int]
LOGGER = Logger('./out/debug.log')


class Node:
    def __init__(self, value: Token):
        self.value = value
        self.children = []

    def evaluate(self, table: SymbolTable) -> int:
        return 0


class Block(Node):

    children: List[Node]

    def __init__(self, value: Token):
        self.value = value
        self.children = []

    def evaluate(self, table: SymbolTable):
        for node in self.children:
            if type(node) is Return:
                return node.evaluate(table)
            node.evaluate(table)

    def addNode(self, node: Node):
        self.children.append(node)


class FuncDef(Node):

    def __init__(self, value):
        super().__init__(value)
        self.arguments = []
        self.statements = []

    def addArgument(self, arg: Node) -> NoReturn:
        LOGGER.logParse(f"[DEBUG] [NODE] [FUNCDEF] Adding argument {arg} to func {self.value.value}")
        self.arguments.append(arg)

    def addStatements(self, statement: Node):
        LOGGER.logParse(f"[DEBUG] [NODE] [FUNCDEF] Adding statement {statement} to func {self.value.value}")
        self.statements.append(statement)

    def evaluate(self, table: SymbolTable):
        LOGGER.logParse(f"[INFO] [NODE] [FUNCDEF] Declaring {self.value.value} to symboltable")
        table.declareVariable(self.value.value, self, "FUNCTION")
        return table


class FuncCall(Node):

    arguments: List[Node] = []

    def __init__(self, value):
        super().__init__(value)
        self.children = [self.arguments]

    def addArgument(self, arg: Node) -> NoReturn:
        self.arguments.append(arg)
        self.children[0] = self.arguments

    def evaluate(self, table: SymbolTable):
        LOGGER.logParse(f"[INFO] [NODE] [FUNCCALL] Calling {self.value.value}.")
        func, tmp = table.getVariable(self.value.value)
        if tmp != 'FUNCTION':
            raise TypeError(f"Invalid function {self.value.value}")
        scopeTable = SymbolTable()
        for variable, value in table.table.items():
            if value['varType'] == 'FUNCTION':
                scopeTable.table[variable] = value
                LOGGER.logParse(f"[INFO] [NODE] [FUNCCALL] Adding {variable} to scopeTable of funccall {self.value.value}")
        
        argResults = []
        for arg in self.arguments:
            argResults.append(arg.evaluate(table))

        if len(argResults) == len(func.arguments):
            for arg, argResult in zip(func.arguments, argResults):
                scopeTable.declareVariable(arg.value.value, argResult[0], argResult[1])
    
        for statement in func.statements:
            LOGGER.logParse(f"[DEBUG] [NODE] [FUNCCALL] Running statement {statement}")
            ret = statement.evaluate(scopeTable)
            if ret is not None:
                return ret


class Return(Node):

    def __init__(self, value, child: Node):
        super().__init__(value)
        self.child = child

    def evaluate(self, table):
        return self.child.evaluate(table)


class Assigner(Node):

    child: Node

    def __init__(self, value: Token, child: Node, varType: str = None):
        self.value = value
        self.child = child
        self.varType = varType
        self.children = [self.value, self.child, self.varType]

    def evaluate(self, table: SymbolTable) -> SymbolTable:
        value = self.child.evaluate(table)
        if self.varType:
            LOGGER.logParse(f"[INFO] [NODE] [ASSIGNER] Declaring {self.value.value}")
            table.declareVariable(self.value.value, value[0], self.varType)
        else:
            LOGGER.logParse(f"[INFO] [NODE] [ASSIGNER] Setting {self.value.value}")
            table.setVariable(self.value.value, value[0], value[1])
        return table


class Print(Node):

    child: Node

    def __init__(self, value: Token, child: Node):
        super().__init__(value)
        self.child = child
        self.children = [child]

    def evaluate(self, table: SymbolTable):
        LOGGER.logParse(f"[INFO] [NODE] [PRINT] Print")
        print(self.child.evaluate(table)[0])


class While(Node):

    condition: Node
    command: Node

    def __init__(self, value, condition: Node, command: Node):
        super().__init__(value)
        self.condition = condition
        self.command = command
        self.children = [self.condition, self.command]

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
        self.children = [self.condition, self.commandTrue]
        self.commandFalse = None

    def setCommandFalse(self, commandFalse: Node) -> NoReturn:
        self.commandFalse = commandFalse
        self.children.append(self.commandFalse)

    def evaluate(self, table):
        if self.condition.value.tokenType == TokenTypes.STRING:
            raise TypeError("If condition should be a Bool")
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
            return  int(value), "int"
        else:
            return  value, "string"


class BinOp(Node):

    aritOperators: List[TokenTypes] = [
        TokenTypes.PLUS,
        TokenTypes.MINUS,
        TokenTypes.MULTIPLIER,
        TokenTypes.DIVIDER,
    ]
    children: List[Node]

    def __init__(self, value: Token, left: Node, right: Node):
        super().__init__(value)
        self.children = [left, right]

    def evaluate(self, table: SymbolTable):
        childrenZero = self.children[0].evaluate(table)
        childrenOne = self.children[1].evaluate(table)
        if (
            (childrenOne[1] == "string" and childrenZero[1] != "string")
            or (childrenOne[1] != "string" and childrenZero[1] == "string")
            or (
                self.value.tokenType in self.aritOperators
                and "string" in [childrenZero[1], childrenOne[1]]
            )
        ):
            raise BufferError("Invalid operation between strings")
        if self.value.tokenType == TokenTypes.PLUS:
            return int(childrenZero[0]) + int(childrenOne[0]), "int"
        elif self.value.tokenType == TokenTypes.MINUS:
            return int(childrenZero[0]) - int(childrenOne[0]), "int"
        elif self.value.tokenType == TokenTypes.MULTIPLIER:
            return int(childrenZero[0]) * int(childrenOne[0]), "int"
        elif self.value.tokenType == TokenTypes.DIVIDER:
            return int(int(childrenZero[0]) / int(childrenOne[0])), "int"
        elif self.value.tokenType == TokenTypes.BOOL_AND:
            return bool(childrenZero[0] and childrenOne[0]), "bool"
        elif self.value.tokenType == TokenTypes.BOOL_OR:
            return bool(childrenZero[0] or childrenOne[0]), "bool"
        elif self.value.tokenType == TokenTypes.BOOL_GT:
            return bool(childrenZero[0] > childrenOne[0]), "bool"
        elif self.value.tokenType == TokenTypes.BOOL_LT:
            return bool(childrenZero[0] < childrenOne[0]), "bool"
        elif self.value.tokenType == TokenTypes.BOOL_EQUAL:
            return bool(childrenZero[0] == childrenOne[0]), "bool"
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
        self.children = [self.child]

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
        return self.value.value, "int"


class BoolVal(Node):
    def __init__(self, value: Token):
        super().__init__(value)

    def evaluate(self, table: SymbolTable):
        return bool(self.value.value), "bool"


class StrVal(Node):
    def __init__(self, value: Token):
        super().__init__(value)

    def evaluate(self, table: SymbolTable):
        return self.value.value, "string"


class NoOp(Node):
    def __init__(self, value: Token):
        super().__init__(value)

    def evaluate(self, table: SymbolTable):
        return 0, "int"
