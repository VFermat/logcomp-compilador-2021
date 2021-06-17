import os


class Logger:
    def __init__(self, logfile):
        super().__init__()
        if not os.path.isdir("out"):
            os.mkdir("out")
        self.logfile = logfile
        self._cleanFiles()

    def _cleanFiles(self):
        with open(self.logfile, "w") as f:
            f.write("")
        with open("./out/ast.log", "w") as f:
            f.write("")

    def logParse(self, msg):
        with open(self.logfile, "a") as f:
            f.write(msg)
            f.write("\n")

    def logAst(self, ast, depth: int = 0):
        with open("./out/ast.log", "a") as f:
            tabs = " " * depth
            f.write(f"{tabs}[Node {ast} ")
            if type(ast) is not list:
                f.write(f"{ast.value.value}")
            f.write(" ]:")
            f.write("\n")
            if type(ast) is list:
                for child in ast:
                    self.logAst(child, depth + 1)
            else:
                for child in ast.children:
                    self.logAst(child, depth + 1)
