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

import Parser, os

test_file_dir = "/home/dave/PycharmProjects/Compiler/testParser/"

if __name__ == "__main__":

    # For every file in the test file directory,
    for f in os.listdir(test_file_dir):

        # Prepend the path of the test file directory
        input_filename = test_file_dir + f

        print("\nParsing file " + f)

        try:
            Parser.Parser.parse(input_filename)
        except Exception as ex:
            print("\nException occurred while parsing file %s:\n%s" % (f, ex))

