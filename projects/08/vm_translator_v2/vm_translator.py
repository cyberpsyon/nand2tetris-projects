import os
import sys
from parser import Parser
from code_writer import CodeWriter

def get_vm_files(path):
    if path.endswith(".vm"):
        return [path]
    else:
        files = [os.path.join(path, f) for f in os.listdir(path) if f.endswith(".vm")]
        if not files:
            raise ValueError("Directory contains no .vm files.")
        return files

def main():
    if len(sys.argv) != 2:
        print("Usage: python vm_translator.py [file.vm | directory]")
        sys.exit(1)

    input_path = sys.argv[1]
    
    try:
        vm_files = get_vm_files(input_path)
    except (ValueError, FileNotFoundError) as e:
        print(f"Error: {e}")
        sys.exit(1)
        
    if os.path.isdir(input_path):
        dir_name = os.path.basename(os.path.normpath(input_path))
        output_path = os.path.join(input_path, f"{dir_name}.asm")
    else:
        output_path = os.path.splitext(input_path)[0] + ".asm"

    writer = CodeWriter(output_path)
    
    # Write bootstrap code only if Sys.vm is present (for staged testing)
    if any("Sys.vm" in f for f in vm_files):
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
            elif ctype == Parser.FUNCTION:
                writer.write_function(parser.arg1(), parser.arg2())
            elif ctype == Parser.CALL:
                writer.write_call(parser.arg1(), parser.arg2())
            elif ctype == Parser.RETURN:
                writer.write_return()

    writer.close()
    print(f"File created: {output_path}")

if __name__ == "__main__":
    main()