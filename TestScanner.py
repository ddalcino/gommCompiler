"""
Filename: TestScanner.py

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

    for f in os.listdir(test_file_dir):
        input_filename = test_file_dir + f
        output_filename = output_dir + f + ".tokens"
        print("Test file is: " + input_filename)
        Scanner.scan_file(input_filename, output_filename)
