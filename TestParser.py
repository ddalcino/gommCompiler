"""
Filename: TestParser.py

David Dalcino
CS 6110
Prof. Reiter
Winter 2017
CSU East Bay

Parser Assignment
Due 2/9/17


This file tests a recursive descent parser.
"""

import ParserWithST, os

test_file_dir = "testPrograms"

if __name__ == "__main__":

    # For every file in the test file directory,
    for f in os.listdir(test_file_dir):

        # Prepend the path of the test file directory
        input_filename = test_file_dir + f

        print("\nParsing file " + f)

        try:
            ParserWithST.Parser.parse(input_filename, asm_output_filename="out.asm")
        except Exception as ex:
            print("\nException occurred while parsing file %s:\n%s" % (f, ex))

