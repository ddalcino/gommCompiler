import Parser, os

test_file_dir = "/home/dave/PycharmProjects/Compiler/unusedTestPrograms/"

if __name__ == "__main__":

    # For every file in the test file directory,
    for f in os.listdir(test_file_dir):

        # Prepend the path of the test file directory
        input_filename = test_file_dir + f

        print("Parsing file " + f)

        try:
            Parser.Parser.parse(input_filename)
        except Exception as ex:
            print("Exception occurred while parsing file %s:\n%s" % (f, ex))

        print("\n\n\n\n")
