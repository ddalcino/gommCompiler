"""
Filename: TestScanner.py
Written in Python 3, interpreted with Python 3.5.1

David Dalcino
CS 6110
Prof. Reiter
Winter 2017
CSU East Bay

Scanner Assignment
Due 1/27/17

This file tests the Scanner class on several test program files.
"""


import os
from Scanner import Scanner

test_file_dir = "/home/dave/PycharmProjects/Compiler/testPrograms/"
output_dir = "/home/dave/PycharmProjects/Compiler/tokenOutput/"

if __name__ == "__main__":

    # For every file in the test file directory,
    for f in os.listdir(test_file_dir):

        # Prepend the path of the test file directory
        input_filename = test_file_dir + f
        # Prepare to make an output file in the output directory
        output_filename = output_dir + f + ".tokens"
        # Print the name of the input file
        print("Test file is: " + input_filename)
        # Scan the file
        Scanner.scan_file(input_filename, output_filename)
