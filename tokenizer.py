from tokens import Token, TokenTypes


class Tokenizer:

    position: str
    position: int
    actual: Token

    def __init__(self, origin: str):
        self.origin = origin
        self.position = 0
        self.actual = None

    def selectNext(self) -> Token:
        if self.position == len(self.origin):
            token = Token(TokenTypes.EOF, 0)
            self.actual = token
            return token
        i = self.position
        while i < len(self.origin):
            char = self.origin[i]
            if char == "+":
                token = Token(TokenTypes.PLUS, 1)
                break
            elif char == "-":
                token = Token(TokenTypes.MINUS, 1)
                break
            elif char == "/":
                token = Token(TokenTypes.DIVIDER, 1)
                break
            elif char == "*":
                token = Token(TokenTypes.MULTIPLIER, 1)
                break
            elif char == ">":
                token = Token(TokenTypes.BOOL_GT, 1)
                break
            elif char == "<":
                token = Token(TokenTypes.BOOL_LT, 1)
                break
            elif char == "=":
                if self.origin[i + 1] == "=":
                    i += 1
                    token = Token(TokenTypes.BOOL_EQUAL, 1)
                else:
                    token = Token(TokenTypes.ASSIGN, 0)
                break
            elif char == "&":
                if self.origin[i + 1] == "&":
                    i += 1
                    token = Token(TokenTypes.BOOL_AND, 1)
                else:
                    raise BufferError(
                        f"Invalid char {char} in position {self.position}"
                    )
                break
            elif char == "|":
                if self.origin[i + 1] == "|":
                    i += 1
                    token = Token(TokenTypes.BOOL_OR, 1)
                else:
                    raise BufferError(
                        f"Invalid char {char} in position {self.position}"
                    )
                break
            elif char == ";":
                token = Token(TokenTypes.SEPARATOR, 0)
                break
            elif char.isdigit():
                temp = char
                if i < len(self.origin) - 1:
                    while self.origin[i + 1].isdigit():
                        char = self.origin[i + 1]
                        i += 1
                        temp += char
                        if i == len(self.origin) - 1:
                            break
                token = Token(TokenTypes.NUMBER, int(temp))
                break
            elif char == "(":
                token = Token(TokenTypes.LPAR, 1)
                break
            elif char == ")":
                token = Token(TokenTypes.RPAR, 1)
                break
            elif char == "{":
                token = Token(TokenTypes.BLOCK_OPENER, 1)
                break
            elif char == "}":
                token = Token(TokenTypes.BLOCK_CLOSER, 1)
                break
            elif char == "!":
                token = Token(TokenTypes.BOOL_NOT, 1)
                break
            elif char == '"':
                temp = char
                if i < len(self.origin) - 1:
                    while self.origin[i + 1] != '"':
                        char = self.origin[i + 1]
                        i += 1
                        temp += char
                        if i == len(self.origin) - 1:
                            break
                i += 1
                token = Token(TokenTypes.STRING, temp[1:])
                break
            elif char == " ":
                i += 1
            elif char.isalpha():
                temp = char
                if i < len(self.origin) - 1:
                    while self.origin[i + 1].isalnum() or self.origin[i + 1] == "_":
                        char = self.origin[i + 1]
                        i += 1
                        temp += char
                        if i == len(self.origin) - 1:
                            break
                if temp == "true":
                    token = Token(TokenTypes.BOOLEAN, True)
                elif temp == "false":
                    token = Token(TokenTypes.BOOLEAN, False)
                else:
                    token = Token(TokenTypes.IDENTIFIER, temp)
                break
            else:
                raise ValueError()
        self.actual = token
        self.position = i + 1
        return token
