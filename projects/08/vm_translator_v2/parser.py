import os

class Parser:
    ARITHMETIC = 0
    PUSH = 1
    POP = 2
    LABEL = 3
    GOTO = 4
    IF = 5
    FUNCTION = 6
    RETURN = 7
    CALL = 8
    ARITHMETIC_CMDS = {"add", "sub", "neg", "eq", "gt", "lt", "and", "or", "not"}

    def __init__(self, file_in):
        try:
            with open(file_in, "r") as f:
                self.cmds = [
                    line.split("//")[0].strip()
                    for line in f
                    if line.split("//")[0].strip()
                ]
            self.index = 0
            self.current_cmd = ""
            self.arg_type = -1
            self.argument1 = ""
            self.argument2 = -1
        except FileNotFoundError:
            print(f"File not found: {file_in}")
            self.cmds = []

    def has_more_commands(self):
        return self.index < len(self.cmds)

    def advance(self):
        self.current_cmd = self.cmds[self.index]
        self.index += 1
        segs = self.current_cmd.split()
        command = segs[0]

        if command in self.ARITHMETIC_CMDS:
            self.arg_type = self.ARITHMETIC
            self.argument1 = command
        elif command == "return":
            self.arg_type = self.RETURN
        else:
            type_map = {
                "push": self.PUSH, "pop": self.POP, "label": self.LABEL,
                "if-goto": self.IF, "goto": self.GOTO, "function": self.FUNCTION,
                "call": self.CALL
            }
            self.arg_type = type_map[command]
            self.argument1 = segs[1]
            if self.arg_type in {self.PUSH, self.POP, self.FUNCTION, self.CALL}:
                self.argument2 = int(segs[2])

    def command_type(self):
        return self.arg_type

    def arg1(self):
        if self.command_type() == self.RETURN:
            raise RuntimeError("arg1() should not be called for RETURN command")
        return self.argument1

    def arg2(self):
        if self.command_type() not in {self.PUSH, self.POP, self.FUNCTION, self.CALL}:
            raise RuntimeError("arg2() not available for this command type")
        return self.argument2

    @staticmethod
    def no_comments(line):
        return line.split("//")[0]