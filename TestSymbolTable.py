__author__ = 'dave'

import os
import FileReader
import SymbolTable

test_file_dir = "/home/dave/PycharmProjects/Compiler/testCode/"
BUFFER_SIZE = 200

if __name__ == "__main__":
    for f in os.listdir(test_file_dir):
        filename = test_file_dir + f
        print("Test file is: " + filename)
        with FileReader.FileReader(filename) as file_reader:   # open file safely
            symbol_table = SymbolTable.SymbolTable()    # symbol table
            symbol_count = 0                    # number unique ids encountered
            token_buffer = ' ' * BUFFER_SIZE    # buffer to hold tokens
            buf_index = 0                       # the index into token_buffer
            state = "Null"                      # the state the DFA is in
            while not file_reader.EOF():

                # Record the next character
                ch = file_reader.get_char()

                if not ch.isspace():
                    if ch == '{':
                        state = "Open Brace"
                        # record Open Brace token
                        symbol_table.open_scope()
                    elif ch == '}':
                        state = "Close Brace"
                        # record Close Brace token
                        symbol_table.close_scope()
                    else:
                        # If it's not space, and not a brace, it's an identifier
                        state = "Identifier"
                        # copy the character into the token buffer
                        token_buffer = token_buffer[:buf_index] + ch + \
                                       token_buffer[buf_index + 1:]
                        # increment buf_index
                        buf_index += 1
                else:
                    # we're in whitespace
                    if state == "Identifier":
                        # record the identifier and go back to null state
                        identifier = token_buffer[:buf_index]
                        # if symbol isn't in the table, insert it
                        if not symbol_table.find(identifier):
                            #print(identifier)
                            symbol_table.insert(identifier,
                                                "scope=%d at pos %d" %
                                                (symbol_table.get_scope_id(),
                                                 symbol_count))
                            symbol_count += 1

                        token_buffer = ' ' * BUFFER_SIZE    # clear buffer
                        buf_index = 0                       # reset index

            symbol_table.display()



