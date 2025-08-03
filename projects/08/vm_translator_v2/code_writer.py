import os
import re
from parser import Parser

class CodeWriter:
    def __init__(self, file_out_path):
        try:
            self.out_file = open(file_out_path, 'w')
            self.file_name = ""
            self.arth_jump_count = 0
            self.return_label_count = 0
        except IOError:
            raise IOError(f"Could not open file for writing: {file_out_path}")

    def set_file_name(self, file_path):
        self.file_name = os.path.splitext(os.path.basename(file_path))[0]

    def write_init(self):
        self.out_file.write("@256\nD=A\n@SP\nM=D\n")
        self.write_call("Sys.init", 0)

    def write_label(self, label):
        self.out_file.write(f"({label})\n")

    def write_goto(self, label):
        self.out_file.write(f"@{label}\n0;JMP\n")

    def write_if(self, label):
        self.out_file.write("@SP\nAM=M-1\nD=M\n" + f"@{label}\nD;JNE\n")

    def write_call(self, function_name, num_args):
        return_label = f"{function_name}$ret.{self.return_label_count}"
        self.return_label_count += 1
        self.out_file.write(f"@{return_label}\nD=A\n@SP\nA=M\nM=D\n@SP\nM=M+1\n")
        for seg in ["LCL", "ARG", "THIS", "THAT"]:
            self.out_file.write(f"@{seg}\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n")
        self.out_file.write(f"@SP\nD=M\n@5\nD=D-A\n@{num_args}\nD=D-A\n@ARG\nM=D\n")
        self.out_file.write("@SP\nD=M\n@LCL\nM=D\n")
        self.write_goto(function_name)
        self.write_label(return_label)

    def write_return(self):
        self.out_file.write("@LCL\nD=M\n@R13\nM=D\n") # R13 (FRAME) = LCL
        self.out_file.write("@5\nA=D-A\nD=M\n@R14\nM=D\n") # R14 (RET) = *(FRAME - 5)
        self.out_file.write("@SP\nAM=M-1\nD=M\n@ARG\nA=M\nM=D\n") # *ARG = pop()
        self.out_file.write("@ARG\nD=M+1\n@SP\nM=D\n") # SP = ARG + 1
        for seg in ["THAT", "THIS", "ARG", "LCL"]:
            self.out_file.write(f"@R13\nAM=M-1\nD=M\n@{seg}\nM=D\n")
        self.out_file.write("@R14\nA=M\n0;JMP\n") # goto RET

    def write_function(self, function_name, num_locals):
        self.write_label(function_name)
        for _ in range(num_locals):
            self.out_file.write("@SP\nA=M\nM=0\n@SP\nM=M+1\n")

    def write_arithmetic(self, command):
        if command == "neg": code = "M=-M\n"
        elif command == "not": code = "M=!M\n"
        else:
            code = "@SP\nAM=M-1\nD=M\nA=A-1\n"
            if command == "add": code += "M=M+D\n"
            elif command == "sub": code += "M=M-D\n"
            elif command == "and": code += "M=M&D\n"
            elif command == "or": code += "M=M|D\n"
            elif command in {"eq", "gt", "lt"}:
                jump_map = {"eq": "JEQ", "gt": "JGT", "lt": "JLT"}
                label = f"COMP.{self.arth_jump_count}"
                self.arth_jump_count += 1
                code += (f"D=M-D\n@{label}.TRUE\nD;{jump_map[command]}\n"
                         f"@SP\nA=M-1\nM=0\n@{label}.END\n0;JMP\n"
                         f"({label}.TRUE)\n@SP\nA=M-1\nM=-1\n({label}.END)\n")
        self.out_file.write(code)

    def write_push_pop(self, command, segment, index):
        if command == Parser.PUSH:
            if segment == "constant":
                self.out_file.write(f"@{index}\nD=A\n")
            else:
                base_map = {"local": "LCL", "argument": "ARG", "this": "THIS", "that": "THAT"}
                if segment in base_map: # Indirect: local, argument, this, that
                    self.out_file.write(f"@{base_map[segment]}\nD=M\n@{index}\nA=D+A\nD=M\n")
                elif segment == "pointer": # Direct: pointer, temp, static
                    self.out_file.write(f"@{'THIS' if index == 0 else 'THAT'}\nD=M\n")
                elif segment == "temp":
                    self.out_file.write(f"@R{5 + index}\nD=M\n")
                elif segment == "static":
                    self.out_file.write(f"@{self.file_name}.{index}\nD=M\n")
            self.out_file.write("@SP\nA=M\nM=D\n@SP\nM=M+1\n")
        elif command == Parser.POP:
            base_map = {"local": "LCL", "argument": "ARG", "this": "THIS", "that": "THAT"}
            if segment in base_map: # Indirect: local, argument, this, that
                self.out_file.write(f"@{base_map[segment]}\nD=M\n@{index}\nD=D+A\n@R13\nM=D\n")
            elif segment == "pointer": # Direct: pointer, temp, static
                self.out_file.write(f"@{('THIS' if index == 0 else 'THAT')}\nD=A\n@R13\nM=D\n")
            elif segment == "temp":
                self.out_file.write(f"@R{5 + index}\nD=A\n@R13\nM=D\n")
            elif segment == "static":
                self.out_file.write(f"@{self.file_name}.{index}\nD=A\n@R13\nM=D\n")
            self.out_file.write("@SP\nAM=M-1\nD=M\n@R13\nA=M\nM=D\n")

    def close(self):
        self.out_file.close()