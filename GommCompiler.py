import sys
import  os
from ParserWithST import Parser

if __name__ == "__main__":
    arg_list = sys.argv[1:]

    if arg_list is None or len(arg_list) == 0:
        print("Usage: python3 GommCompiler.py source_code.gomm {"
              "more_source_files.gomm}")

    list_of_failed_compilations = []
    # For every file in the argument list,
    for f in sys.argv:
        success = False

        input_filename = f

        # Output filename: add extension .asm
        asm_out = f + ".asm"
        # If there was an extension, replace it instead
        if '.' in f:
            asm_out = '.'.join(f.split('.')[:-1]) + ".asm"

        print("\nParsing file " + f)

        try:
            success = Parser.parse(input_filename, asm_out)
        except Exception as ex:
            print("\nException occurred while parsing file %s:\n%s" % (f, ex))


        if not success:
            os.remove(asm_out)
            list_of_failed_compilations.append(f)
    if len(list_of_failed_compilations) > 0:
        print("The following file(s) failed to compile:")
        for f in list_of_failed_compilations:
            print(f)
    else:
        print("All files compiled successfully!")

