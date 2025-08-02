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

    arithmetic_cmds = [
        "add", "sub", "neg", "eq", "gt", "lt", "and", "or", "not"
    ]

    def __init__(self, file_in):
        self.cmds = []
        self.current_cmd = ""
        self.arg_type = -1
        self.argument1 = ""
        self.argument2 = -1

        try:
            with open(file_in, "r") as f:
                lines = f.readlines()
                preprocessed = [
                    self.no_comments(line).strip()
                    for line in lines
                    if self.no_comments(line).strip()
                ]
                self.cmds = preprocessed
                self.index = 0
        except FileNotFoundError:
            print("File not found!")

    def has_more_commands(self):
        return self.index < len(self.cmds)

    def advance(self):
        self.current_cmd = self.cmds[self.index]
        self.index += 1
        self.argument1 = ""
        self.argument2 = -1

        segs = self.current_cmd.split()

        if len(segs) > 3:
            raise ValueError("Too many arguments!")

        if segs[0] in self.arithmetic_cmds:
            self.arg_type = self.ARITHMETIC
            self.argument1 = segs[0]
        elif segs[0] == "return":
            self.arg_type = self.RETURN
            self.argument1 = segs[0]
        else:
            self.argument1 = segs[1]
            if segs[0] == "push":
                self.arg_type = self.PUSH
            elif segs[0] == "pop":
                self.arg_type = self.POP
            elif segs[0] == "label":
                self.arg_type = self.LABEL
            elif segs[0] == "if-goto":
                self.arg_type = self.IF
            elif segs[0] == "goto":
                self.arg_type = self.GOTO
            elif segs[0] == "function":
                self.arg_type = self.FUNCTION
            elif segs[0] == "call":
                self.arg_type = self.CALL
            else:
                raise ValueError("Unknown command type")

            if self.arg_type in {self.PUSH, self.POP, self.FUNCTION, self.CALL}:
                try:
                    self.argument2 = int(segs[2])
                except:
                    raise ValueError("Argument2 must be an integer")

    def command_type(self):
        if self.arg_type != -1:
            return self.arg_type
        else:
            raise RuntimeError("No command")

    def arg1(self):
        if self.command_type() != self.RETURN:
            return self.argument1
        else:
            raise RuntimeError("arg1 should not be called for RETURN command")

    def arg2(self):
        if self.command_type() in {self.PUSH, self.POP, self.FUNCTION, self.CALL}:
            return self.argument2
        else:
            raise RuntimeError("arg2 not available for this command type")

    @staticmethod
    def no_comments(line):
        return line.split("//")[0]

    @staticmethod
    def no_spaces(s):
        return ''.join(s.split())

    @staticmethod
    def get_ext(filename):
        if '.' in filename:
            return filename[filename.rindex('.'):]
        return ''
