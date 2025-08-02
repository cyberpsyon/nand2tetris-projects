import re
from parser import Parser

class CodeWriter:
    label_cnt = 0

    def __init__(self, file_out):
        self.arth_jump_flag = 0
        self.out_printer = open(file_out, 'w')
        self.file_name = self._strip_ext(file_out)

    def _strip_ext(self, path):
        return re.sub(r"\.[^.]+$", "", path.split("/")[-1])

    def set_file_name(self, file_path):
        self.file_name = self._strip_ext(file_path)

    def write_arithmetic(self, command):
        if command == "add":
            self.out_printer.write(self.arithmetic_template1() + "M=M+D\n")
        elif command == "sub":
            self.out_printer.write(self.arithmetic_template1() + "M=M-D\n")
        elif command == "and":
            self.out_printer.write(self.arithmetic_template1() + "M=M&D\n")
        elif command == "or":
            self.out_printer.write(self.arithmetic_template1() + "M=M|D\n")
        elif command == "gt":
            self.out_printer.write(self.arithmetic_template2("JLE"))
            self.arth_jump_flag += 1
        elif command == "lt":
            self.out_printer.write(self.arithmetic_template2("JGE"))
            self.arth_jump_flag += 1
        elif command == "eq":
            self.out_printer.write(self.arithmetic_template2("JNE"))
            self.arth_jump_flag += 1
        elif command == "not":
            self.out_printer.write("@SP\nA=M-1\nM=!M\n")
        elif command == "neg":
            self.out_printer.write("D=0\n@SP\nA=M-1\nM=D-M\n")
        else:
            raise ValueError("Invalid arithmetic command")

    def write_push_pop(self, command, segment, index):
        if command == Parser.PUSH:
            if segment == "constant":
                self.out_printer.write(f"@{index}\nD=A\n@SP\nA=M\nM=D\n@SP\nM=M+1\n")
            elif segment in ["local", "argument", "this", "that"]:
                base = {"local": "LCL", "argument": "ARG", "this": "THIS", "that": "THAT"}[segment]
                self.out_printer.write(self.push_template1(base, index, False))
            elif segment == "temp":
                self.out_printer.write(self.push_template1("R5", index + 5, False))
            elif segment == "pointer" and index in (0, 1):
                self.out_printer.write(self.push_template1("THIS" if index == 0 else "THAT", index, True))
            elif segment == "static":
                self.out_printer.write(f"@{self.file_name}{index}\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n")
        elif command == Parser.POP:
            if segment in ["local", "argument", "this", "that"]:
                base = {"local": "LCL", "argument": "ARG", "this": "THIS", "that": "THAT"}[segment]
                self.out_printer.write(self.pop_template1(base, index, False))
            elif segment == "temp":
                self.out_printer.write(self.pop_template1("R5", index + 5, False))
            elif segment == "pointer" and index in (0, 1):
                self.out_printer.write(self.pop_template1("THIS" if index == 0 else "THAT", index, True))
            elif segment == "static":
                self.out_printer.write(f"@{self.file_name}{index}\nD=A\n@R13\nM=D\n@SP\nAM=M-1\nD=M\n@R13\nA=M\nM=D\n")
        else:
            raise ValueError("Invalid push/pop command")

    def write_label(self, label):
        if re.match(r"^[^0-9][0-9A-Za-z_:.\$]+$", label):
            self.out_printer.write(f"({label})\n")
        else:
            raise ValueError("Invalid label format")

    def write_goto(self, label):
        if re.match(r"^[^0-9][0-9A-Za-z_:.\$]+$", label):
            self.out_printer.write(f"@{label}\n0;JMP\n")
        else:
            raise ValueError("Invalid label format")

    def write_if(self, label):
        if re.match(r"^[^0-9][0-9A-Za-z_:.\$]+$", label):
            self.out_printer.write(self.arithmetic_template1() + f"@{label}\nD;JNE\n")
        else:
            raise ValueError("Invalid label format")

    def write_init(self):
        self.out_printer.write("@256\nD=A\n@SP\nM=D\n")
        self.write_call("Sys.init", 0)

    def write_call(self, function_name, num_args):
        label = f"RETURN_LABEL{CodeWriter.label_cnt}"
        CodeWriter.label_cnt += 1
        self.out_printer.write(f"@{label}\nD=A\n@SP\nA=M\nM=D\n@SP\nM=M+1\n")
        for segment in ["LCL", "ARG", "THIS", "THAT"]:
            self.out_printer.write(self.push_template1(segment, 0, True))
        self.out_printer.write(f"@SP\nD=M\n@5\nD=D-A\n@{num_args}\nD=D-A\n@ARG\nM=D\n")
        self.out_printer.write("@SP\nD=M\n@LCL\nM=D\n")
        self.out_printer.write(f"@{function_name}\n0;JMP\n({label})\n")

    def write_return(self):
        self.out_printer.write(self.return_template())

    def write_function(self, function_name, num_locals):
        self.out_printer.write(f"({function_name})\n")
        for _ in range(num_locals):
            self.write_push_pop(Parser.PUSH, "constant", 0)

    def return_template(self):
        return ("@LCL\nD=M\n@R11\nM=D\n@5\nA=D-A\nD=M\n@R12\nM=D\n" +
                self.pop_template1("ARG", 0, False) +
                "@ARG\nD=M\n@SP\nM=D+1\n" +
                self.pre_frame_template("THAT") +
                self.pre_frame_template("THIS") +
                self.pre_frame_template("ARG") +
                self.pre_frame_template("LCL") +
                "@R12\nA=M\n0;JMP\n")

    def pre_frame_template(self, position):
        return f"@R11\nD=M-1\nAM=D\nD=M\n@{position}\nM=D\n"

    def arithmetic_template1(self):
        return "@SP\nAM=M-1\nD=M\nA=A-1\n"

    def arithmetic_template2(self, jump_type):
        label = self.arth_jump_flag
        return ("@SP\nAM=M-1\nD=M\nA=A-1\nD=M-D\n" +
                f"@FALSE{label}\nD;{jump_type}\n" +
                "@SP\nA=M-1\nM=-1\n" +
                f"@CONTINUE{label}\n0;JMP\n" +
                f"(FALSE{label})\n@SP\nA=M-1\nM=0\n(CONTINUE{label})\n")

    def push_template1(self, segment, index, is_direct):
        code = "" if is_direct else f"@{index}\nA=D+A\nD=M\n"
        return f"@{segment}\nD=M\n{code}@SP\nA=M\nM=D\n@SP\nM=M+1\n"

    def pop_template1(self, segment, index, is_direct):
        code = "D=A\n" if is_direct else f"D=M\n@{index}\nD=D+A\n"
        return f"@{segment}\n{code}@R13\nM=D\n@SP\nAM=M-1\nD=M\n@R13\nA=M\nM=D\n"

    def close(self):
        self.out_printer.close()
