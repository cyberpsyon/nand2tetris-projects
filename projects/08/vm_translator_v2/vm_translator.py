import os
import sys
from parser import Parser
from code_writer import CodeWriter

def get_vm_files(directory):
    return [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith(".vm")]

def main():
    if len(sys.argv) != 2:
        print("Usage: python vm_translator.py [filename.vm | directory]")
        sys.exit(1)

    input_path = sys.argv[1]
    vm_files = []
    file_out_path = ""

    if os.path.isfile(input_path):
        if not input_path.endswith(".vm"):
            raise ValueError("A .vm file is required!")
        vm_files = [input_path]
        file_out_path = input_path.replace(".vm", ".asm")
    elif os.path.isdir(input_path):
        vm_files = get_vm_files(input_path)
        if not vm_files:
            raise ValueError("No .vm files in the directory.")
        abs_path = os.path.abspath(input_path)
        base = os.path.basename(abs_path)
        file_out_path = os.path.join(abs_path, base + ".asm")
    else:
        raise FileNotFoundError("Provided path is not valid.")

    writer = CodeWriter(file_out_path)
    writer.write_init()

    for vm_file in vm_files:
        writer.set_file_name(vm_file)
        parser = Parser(vm_file)

        while parser.has_more_commands():
            parser.advance()
            ctype = parser.command_type()

            if ctype == Parser.ARITHMETIC:
                writer.write_arithmetic(parser.arg1())
            elif ctype in {Parser.PUSH, Parser.POP}:
                writer.write_push_pop(ctype, parser.arg1(), parser.arg2())
            elif ctype == Parser.LABEL:
                writer.write_label(parser.arg1())
            elif ctype == Parser.GOTO:
                writer.write_goto(parser.arg1())
            elif ctype == Parser.IF:
                writer.write_if(parser.arg1())
            elif ctype == Parser.RETURN:
                writer.write_return()
            elif ctype == Parser.FUNCTION:
                writer.write_function(parser.arg1(), parser.arg2())
            elif ctype == Parser.CALL:
                writer.write_call(parser.arg1(), parser.arg2())

    writer.close()
    print(f"File created: {file_out_path}")

if __name__ == "__main__":
    main()
