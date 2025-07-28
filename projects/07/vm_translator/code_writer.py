import parser as p_module
import os

class CodeWriter:
    def __init__(self, file_out_path):
        try:
            self.output_file = open(file_out_path, 'w')
            self.arth_jump_flag = 0
            self.current_file_name = ""
        except IOError as e:
            print(f"Error opening file: {e}")
            self.output_file = None

    def set_file_name(self, file_name):
        self.current_file_name = os.path.basename(file_name).replace(".vm", "")

    def write_arithmetic(self, command):
        if not self.output_file: return
        
        if command in {"add", "sub", "and", "or"}:
            op_map = {"add": "M=M+D", "sub": "M=M-D", "and": "M=M&D", "or": "M=M|D"}
            self.output_file.write(self._arithmetic_template1() + op_map[command] + "\n")
        elif command in {"eq", "gt", "lt"}:
            jump_map = {"eq": "JNE", "gt": "JLE", "lt": "JGE"}
            self.output_file.write(self._arithmetic_template2(jump_map[command]))
            self.arth_jump_flag += 1
        elif command == "not":
            self.output_file.write("@SP\nA=M-1\nM=!M\n")
        elif command == "neg":
            self.output_file.write("D=0\n@SP\nA=M-1\nM=D-M\n")

    def write_push_pop(self, command, segment, index):
        if not self.output_file: return
            
        if command == p_module.Parser.PUSH:
            if segment == "constant":
                self.output_file.write(f"@{index}\nD=A\n@SP\nA=M\nM=D\n@SP\nM=M+1\n")
            elif segment == "local": self.output_file.write(self._push_template1("LCL", index, False))
            elif segment == "argument": self.output_file.write(self._push_template1("ARG", index, False))
            elif segment == "this": self.output_file.write(self._push_template1("THIS", index, False))
            elif segment == "that": self.output_file.write(self._push_template1("THAT", index, False))
            elif segment == "temp": self.output_file.write(self._push_template1("R5", index + 5, False))
            elif segment == "pointer" and index == 0: self.output_file.write(self._push_template1("THIS", index, True))
            elif segment == "pointer" and index == 1: self.output_file.write(self._push_template1("THAT", index, True))
            elif segment == "static": self.output_file.write(self._push_template1(f"{self.current_file_name}.{index}", index, True))
        
        elif command == p_module.Parser.POP:
            if segment == "local": self.output_file.write(self._pop_template1("LCL", index, False))
            elif segment == "argument": self.output_file.write(self._pop_template1("ARG", index, False))
            elif segment == "this": self.output_file.write(self._pop_template1("THIS", index, False))
            elif segment == "that": self.output_file.write(self._pop_template1("THAT", index, False))
            elif segment == "temp": self.output_file.write(self._pop_template1("R5", index + 5, False))
            elif segment == "pointer" and index == 0: self.output_file.write(self._pop_template1("THIS", index, True))
            elif segment == "pointer" and index == 1: self.output_file.write(self._pop_template1("THAT", index, True))
            elif segment == "static": self.output_file.write(self._pop_template1(f"{self.current_file_name}.{index}", index, True))

    def close(self):
        if self.output_file: self.output_file.close()

    def _arithmetic_template1(self):
        return "@SP\nAM=M-1\nD=M\nA=A-1\n"

    def _arithmetic_template2(self, jump_type):
        label_num = self.arth_jump_flag
        return (f"@SP\nAM=M-1\nD=M\nA=A-1\nD=M-D\n@FALSE{label_num}\n"
                f"D;{jump_type}\n@SP\nA=M-1\nM=-1\n@CONTINUE{label_num}\n0;JMP\n"
                f"(FALSE{label_num})\n@SP\nA=M-1\nM=0\n(CONTINUE{label_num})\n")
    
    def _push_template1(self, segment, index, is_direct):
        addr_code = "D=M\n" if not is_direct else "D=A\n"
        no_pointer_code = "" if is_direct else f"@{index}\nA=D+A\nD=M\n"
        if segment in {"LCL", "ARG", "THIS", "THAT"}: addr_code = "D=M\n"
        
        return (f"@{segment}\n{addr_code}{no_pointer_code}"
                f"@SP\nA=M\nM=D\n@SP\nM=M+1\n")

    def _pop_template1(self, segment, index, is_direct):
        no_pointer_code = "D=A\n" if is_direct else f"D=M\n@{index}\nD=D+A\n"
        return (f"@{segment}\n{no_pointer_code}@R13\nM=D\n@SP\nAM=M-1\n"
                f"D=M\n@R13\nA=M\nM=D\n")