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
    
    if os.path.isfile(input_path):
        if not input_path.endswith(".vm"):
            raise ValueError("A .vm file is required!")
        vm_files = [input_path]
        file_out_path = os.path.splitext(input_path)[0] + ".asm"
    elif os.path.isdir(input_path):
        vm_files = get_vm_files(input_path)
        if not vm_files:
            raise ValueError("No .vm files in the directory.")
        dir_name = os.path.basename(os.path.normpath(input_path))
        file_out_path = os.path.join(input_path, f"{dir_name}.asm")
    else:
        raise FileNotFoundError(f"Provided path '{input_path}' is not a valid file or directory.")

    writer = CodeWriter(file_out_path)

    for vm_file in vm_files:
        parser = Parser(vm_file)
        writer.set_file_name(vm_file)
        
        while parser.has_more_commands():
            parser.advance()
            ctype = parser.command_type()

            if ctype == Parser.ARITHMETIC:
                writer.write_arithmetic(parser.arg1())
            elif ctype in {Parser.PUSH, Parser.POP}:
                writer.write_push_pop(ctype, parser.arg1(), parser.arg2())

    writer.close()
    print(f"File created: {file_out_path}")

if __name__ == "__main__":
    main()