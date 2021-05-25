from typing import List, NoReturn, Union
from tokens import Token, TokenTypes
from symbolTable import SymbolTable
from logger import Logger


VARTYPES = Union[str, bool, int]


class Node:
    i: int = 0

    logger: Logger = Logger()

    def __init__(self, value: Token):
        self.value = value
        self.children = []
        self.i = self.increaseId()

    def evaluate(self, table: SymbolTable) -> int:
        return 0

    def increaseId(self) -> int:
        Node.i += 1
        return Node.i


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
        if self.varType:
            self.logger.log(f"PUSH DWORD 0 ; Dim {self.value.value} as {self.varType}")
            value = self.child.evaluate(table)
            variableId = table.declareVariable(self.value.value, value[0], self.varType)
            if value[0]:
                self.logger.log(f"MOV [EBP-{variableId*4}], EBX ; {self.value.value} = {value[0]}")
        else:
            value = self.child.evaluate(table)
            table.setVariable(self.value.value, value[0], value[1])
            variableId = table.setVariable(self.value.value, value[0], value[1])
            self.logger.log(f"MOV [EBP-{variableId*4}], EBX ; {self.value.value} = {value[0]}")
        return table


class Print(Node):

    child: Node

    def __init__(self, value: Token, child: Node):
        super().__init__(value)
        self.child = child

    def evaluate(self, table: SymbolTable):
        result = self.child.evaluate(table)
        self.logger.log("""
PUSH EBX ;
CALL print ; calls print function
POP EBX ;
        """)
        # print(result[0])


class While(Node):

    condition: Node
    command: Node

    def __init__(self, value, condition: Node, command: Node):
        super().__init__(value)
        self.condition = condition
        self.command = command

    def evaluate(self, table):
        self.logger.log(f"LOOP_{self.i}:")
        self.condition.evaluate(table)
        self.logger.log(f"CMP EBX, False ; verifies if test is false")
        self.logger.log(f"JE EXIT_{self.i} ; if test is false, exits")
        self.command.evaluate(table)
        self.logger.log(f"JMP LOOP_{self.i} ; Loops to begin of loop")
        self.logger.log(f"EXIT_{self.i}:")
        # while self.condition.evaluate(table)[0]:
        #     self.command.evaluate(table)


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
        if self.condition.value.tokenType == TokenTypes.STRING:
            raise TypeError("If condition should be a Bool")
        self.condition.evaluate(table)[0]
        self.logger.log(f"CMP EBX, False ; verifies if test is false")
        if self.commandFalse is not None:
            self.logger.log(f"JE ELSE_{self.i} ; if test is false, go to else")
        else:
            self.logger.log(f"JE EXIT_{self.i} ; if test is false, exits")
        self.commandTrue.evaluate(table)
        self.logger.log(f"JMP EXIT_{self.i} ;")
        if self.commandFalse is not None:
            self.logger.log(f"ELSE_{self.i}:")
            self.commandFalse.evaluate(table)
        self.logger.log(f"EXIT_{self.i}: ;")
        # if self.condition.evaluate(table)[0]:
        #     return self.commandTrue.evaluate(table)
        #     return self.commandFalse.evaluate(table)


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
        self.logger.log("PUSH EBX ; BinOp pushes child0 into pile")
        childrenOne = self.children[1].evaluate(table)
        self.logger.log("POP EAX ; BinOp pops child0 from pile")
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
            self.logger.log("ADD EAX, EBX ; BinOp Adds both children")
            result = (int(childrenZero[0]) + int(childrenOne[0]), "int")
        elif self.value.tokenType == TokenTypes.MINUS:
            self.logger.log("SUB EAX, EBX ; BinOp subtracts both children")
            result = (int(childrenZero[0]) - int(childrenOne[0]), "int")
        elif self.value.tokenType == TokenTypes.MULTIPLIER:
            self.logger.log("IMUL EBX ; BinOp multiply both children")
            result = (int(childrenZero[0]) * int(childrenOne[0]), "int")
        elif self.value.tokenType == TokenTypes.DIVIDER:
            self.logger.log("DIV EAX, EBX ; BinOp divides both children")
            result = (int(int(childrenZero[0]) / int(childrenOne[0])), "int")
        elif self.value.tokenType == TokenTypes.BOOL_AND:
            self.logger.log("AND EAX, EBX ; BinOp subtracts both children")
            result = (bool(childrenZero[0] and childrenOne[0]), "bool")
        elif self.value.tokenType == TokenTypes.BOOL_OR:
            self.logger.log("OR EAX, EBX ; BinOp subtracts both children")
            result = (bool(childrenZero[0] or childrenOne[0]), "bool")
        elif self.value.tokenType == TokenTypes.BOOL_GT:
            self.logger.log("CMP EAX, EBX ; BinOp subtracts both children")
            self.logger.log("CALL binop_jg")
            result = (bool(childrenZero[0] > childrenOne[0]), "bool")
        elif self.value.tokenType == TokenTypes.BOOL_LT:
            self.logger.log("CMP EAX, EBX ; BinOp subtracts both children")
            self.logger.log("CALL binop_jl")
            result = (bool(childrenZero[0] < childrenOne[0]), "bool")
        elif self.value.tokenType == TokenTypes.BOOL_EQUAL:
            self.logger.log("CMP EAX, EBX ; BinOp subtracts both children")
            self.logger.log("CALL binop_je")
            result = (bool(childrenZero[0] == childrenOne[0]), "bool")
        else:
            raise BufferError()
        
        self.logger.log("MOV EBX, EAX ; BinOp returns to EBX")
        return result

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
        self.logger.log("PUSH 0 ; UnOp pushes 0 from pile")
        child = self.child.evaluate(table)
        self.logger.log("POP EAX ; UnOp pops 0 from pile")
        if self.value.tokenType == TokenTypes.PLUS:
            self.logger.log("ADD EAX, EBX ; UnOp adds both children")
            result = (+child[0], child[1])
        elif self.value.tokenType == TokenTypes.MINUS:
            self.logger.log("SUB EAX, EBX ; UnOp subtracts both children")
            result = (-child[0], child[1])
        elif self.value.tokenType == TokenTypes.BOOL_NOT:
            result = (not child[0], child[1])
        else:
            raise BufferError()

        self.logger.log("MOV EBX, EAX ; UnOp returns to EBX")
        return result


class IdentifierVal(Node):
    def __init__(self, value: Token):
        super().__init__(value)

    def evaluate(self, table: SymbolTable):
        variable = table.getVariable(self.value.value)
        self.logger.log(f"MOV EBX, [EBP-{variable[2]*4}] ; IdentifierVal loads identifier to EBX")
        return table.getVariable(self.value.value)


class IntVal(Node):
    def __init__(self, value: Token):
        super().__init__(value)

    def evaluate(self, table: SymbolTable):
        self.logger.log(f"MOV EBX, {self.value.value} ; IntVal loads value to EBX")
        return self.value.value, "int"


class BoolVal(Node):
    def __init__(self, value: Token):
        super().__init__(value)

    def evaluate(self, table: SymbolTable):
        self.logger.log(f"MOV EBX, {bool(self.value.value)} ; BoolVal loads value to EBX")
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
        return None, "int"
