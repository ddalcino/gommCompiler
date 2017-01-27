"""
Filename: Scanner.py

David Dalcino
CS 6110
Prof. Reiter
Winter 2017
CSU East Bay

Scanner Assignment
Due 1/27/17


This file implements a scanner, using the most direct translation of a DFA into
code as I could make. In an effort to decouple the code from the design of
the language, and to make the language easier to change, I moved all state
transitions out of the code and into a data structure called 'delta,'
for 'delta transitions,' composed of nested dictionaries. Additionally,
a dictionary called 'token_type_for_accept_state' is used both to define the
list of accept states and to choose what kind of token to make once an
accept state has been reached.

Please note that in an effort to reduce the size of the delta data structure,
I have omitted all transitions to the sink state on illegal characters. Some
states (like comment and string) have transitions on almost every character
into a non-sink state; to save space, I have used the constant 'ANYTHING_ELSE'
to represent these transitions, and implemented any exceptions to the
'ANYTHING_ELSE' rule as usual.
"""

from FileReader import FileReader
from Token import TokenType as tt, Token


class NotScannable:
    """
    Dummy class used for the ANYTHING_ELSE constant; meant to separate it from
    characters that can be scanned in an input file.
    """
    pass

# The ANYTHING_ELSE constant is used to handle transitions for
# any character not defined in the list of possible transitions,
# when such characters are not meant to send us to the sink
# state. For example, comments and strings are meant to allow any
# character except for '\n' or '"', which would terminate the token.
ANYTHING_ELSE = NotScannable()

delta = {
    # delta: a data structure that represents a delta function in a DFA. 
    # The outer dictionary's keys are states of the DFA, while the dictionaries 
    # that these keys refer to contain a list of characters to accept next, 
    # and what state to move to upon reading that character. 
    
    # The expression 'delta[current_state][character_encountered]' would 
    # resolve to the state that the DFA should move into.
    
    # Transitions to a sink state have been omitted, and may be inferred by 
    # their absence if the previous state was not an accept state.

    # Design note: Some minimal amount of performance gains could be made by
    # changing the datatype of the states to an enum or integral type,
    # but I was unable to settle on a solution that I liked that was as
    # readable as this.

    "Start": {
        "0": "Integer_Accept",          "1": "Integer_Accept",
        "2": "Integer_Accept",          "3": "Integer_Accept",
        "4": "Integer_Accept",          "5": "Integer_Accept",
        "6": "Integer_Accept",          "7": "Integer_Accept",
        "8": "Integer_Accept",          "9": "Integer_Accept",

        "_": "ID",
        "A": "ID",      "B": "ID",      "C": "ID",      "D": "ID",
        "E": "ID",      "F": "ID",      "G": "ID",      "H": "ID",
        "I": "ID",      "J": "ID",      "K": "ID",      "L": "ID",
        "M": "ID",      "N": "ID",      "O": "ID",      "P": "ID",
        "Q": "ID",      "R": "ID",      "S": "ID",      "T": "ID",
        "U": "ID",      "V": "ID",      "W": "ID",      "X": "ID",
        "Y": "ID",      "Z": "ID",
        "a": "ID",      "b": "ID",      "c": "ID",      "d": "ID",
        "e": "ID",      "f": "ID",      "g": "ID",      "h": "ID",
        "i": "ID",      "j": "ID",      "k": "ID",      "l": "ID",
        "m": "ID",      "n": "ID",      "o": "ID",      "p": "ID",
        "q": "ID",      "r": "ID",      "s": "ID",      "t": "ID",
        "u": "ID",      "v": "ID",      "w": "ID",      "x": "ID",
        "y": "ID",      "z": "ID",
        
        "#": "Comment",
        "\"": "String_Unfinished",

        # Special characters that could be part of a multi-character token
        "=": "Assignment_Accept",
        "!": "Bang",
        "<": "LessThan_Accept",

        # Special characters that can only be a single-character token
        "+": "Add_Accept",              "-": "Subtract_Accept",
        "*": "Multiply_Accept",         "/": "Divide_Accept",
        "%": "Modulus_Accept",
        "(": "OpenParen_Accept",        ")": "CloseParen_Accept",
        "[": "OpenBracket_Accept",      "]": "CloseBracket_Accept",
        "{": "OpenCurly_Accept",        "}": "CloseCurly_Accept",
        ";": "Semicolon_Accept",        ",": "Comma_Accept",
    },
    "Integer_Accept": {
        "0": "Integer_Accept",          "1": "Integer_Accept",
        "2": "Integer_Accept",          "3": "Integer_Accept",
        "4": "Integer_Accept",          "5": "Integer_Accept",
        "6": "Integer_Accept",          "7": "Integer_Accept",
        "8": "Integer_Accept",          "9": "Integer_Accept",
        ".": "Float_Unfinished"
    },
    "Float_Unfinished": {
        "0": "Float_Accept",            "1": "Float_Accept",
        "2": "Float_Accept",            "3": "Float_Accept",
        "4": "Float_Accept",            "5": "Float_Accept",
        "6": "Float_Accept",            "7": "Float_Accept",
        "8": "Float_Accept",            "9": "Float_Accept",
    },
    "Float_Accept": {
        "0": "Float_Accept",            "1": "Float_Accept",
        "2": "Float_Accept",            "3": "Float_Accept",
        "4": "Float_Accept",            "5": "Float_Accept",
        "6": "Float_Accept",            "7": "Float_Accept",
        "8": "Float_Accept",            "9": "Float_Accept",
    },
    "ID": {
        "_": "ID",
        "0": "ID",      "1": "ID",      "2": "ID",      "3": "ID",
        "4": "ID",      "5": "ID",      "6": "ID",      "7": "ID",
        "8": "ID",      "9": "ID",
        "A": "ID",      "B": "ID",      "C": "ID",      "D": "ID",
        "E": "ID",      "F": "ID",      "G": "ID",      "H": "ID",
        "I": "ID",      "J": "ID",      "K": "ID",      "L": "ID",
        "M": "ID",      "N": "ID",      "O": "ID",      "P": "ID",
        "Q": "ID",      "R": "ID",      "S": "ID",      "T": "ID",
        "U": "ID",      "V": "ID",      "W": "ID",      "X": "ID",
        "Y": "ID",      "Z": "ID",
        "a": "ID",      "b": "ID",      "c": "ID",      "d": "ID",
        "e": "ID",      "f": "ID",      "g": "ID",      "h": "ID",
        "i": "ID",      "j": "ID",      "k": "ID",      "l": "ID",
        "m": "ID",      "n": "ID",      "o": "ID",      "p": "ID",
        "q": "ID",      "r": "ID",      "s": "ID",      "t": "ID",
        "u": "ID",      "v": "ID",      "w": "ID",      "x": "ID",
        "y": "ID",      "z": "ID",
    },

    "Comment": {
        # A special case: Any character except for \n goes back to the
        # Comment state. Transitions are omitted for brevity.
        "\n": "Comment_Accept",
        ANYTHING_ELSE: "Comment"
    },

    "String_Unfinished": {
        "\"": "String_Accept",
        "\\": "String_Escaped_Character",
        "\n": "Sink_State",
        ANYTHING_ELSE: "String_Unfinished"
    },
    "String_Escaped_Character": {
        "\n": "Sink_State",
        ANYTHING_ELSE: "String_Unfinished"
    },
    "String_Accept": {},
    "Comment_Accept": {},

    "Assignment_Accept": {
        "=": "Equals_Accept"
    },
    "Bang": {
        "=": "NotEquals_Accept"
    },
    "LessThan_Accept": {
        "=": "LessThanEquals_Accept"
    },
    "NotEquals_Accept": {},
    "Equals_Accept": {},
    "LessThanEquals_Accept": {},

    # Special characters that can only be a single-character token and have
    # no valid transitions
    "Add_Accept": {},               "Subtract_Accept": {},
    "Multiply_Accept": {},          "Divide_Accept": {},
    "Modulus_Accept": {},
    "OpenParen_Accept": {},         "CloseParen_Accept": {},
    "OpenBracket_Accept": {},       "CloseBracket_Accept": {},
    "OpenCurly_Accept": {},         "CloseCurly_Accept": {},
    "Semicolon_Accept": {},         "Comma_Accept": {},

    # No valid transitions out of the sink state
    "Sink_State": {},
}

# Defines which token type to create for each accept state
token_type_for_accept_state = {
    "Integer_Accept":       tt.Integer,
    "Float_Accept":         tt.Float,
    "ID":                   tt.Identifier,
    "String_Accept":        tt.String,
    "Comment_Accept":       tt.Comment,     # these tokens will be ignored

    "Assignment_Accept":    tt.AssignmentOperator,
    "Equals_Accept":        tt.EqualityOperator,
    "NotEquals_Accept":     tt.NotEqualOperator,
    "LessThan_Accept":      tt.LessThanOperator,
    "LessThanEquals_Accept": tt.LessThanOrEqualOp,

    # Special characters that can only be a single-character token
    "Add_Accept":           tt.AddOperator,
    "Subtract_Accept":      tt.SubtractOperator,
    "Multiply_Accept":      tt.MultiplyOperator,
    "Divide_Accept":        tt.DivideOperator,
    "Modulus_Accept":       tt.ModulusOperator,
    "OpenParen_Accept":     tt.OpenParen,
    "CloseParen_Accept":    tt.CloseParen,
    "OpenBracket_Accept":   tt.OpenBracket,
    "CloseBracket_Accept":  tt.CloseBracket,
    "OpenCurly_Accept":     tt.OpenCurly,
    "CloseCurly_Accept":    tt.CloseCurly,
    "Semicolon_Accept":     tt.Semicolon,
    "Comma_Accept":         tt.Comma,
}

# List of token types that could be returned by get_token, but will be
# filtered out. At this point, only comments are ignored.
ignored_token_t = (tt.Comment, )


# Reserved words:

# List of keywords
keywords = ("if", "else", "while", "func", "return", "int", "float", "char")

# List of built-in functions
built_in_functions = ("print", "prints", "read_int", "read_float", "read_char")



class Scanner:
    """
    A static class, used to scan an input file for tokens
    """

    @staticmethod
    def scan_file(input_filename, output_filename=None):
        """
        Scans an input file and prints the tokens in it
        :param input_filename:  The name of the file to scan
        :param output_filename: The name of the output file. If unassigned,
                                this will be the same as the input filename,
                                with '.tokens' appended
        :return:                None
        """
        if not output_filename:
            output_filename = input_filename + ".tokens"
        with FileReader(input_filename) as fr:
            with open(output_filename, 'w') as file_out:

                time_to_stop = False    # guard condition used to decide when
                                        # to stop reading a file
                while not time_to_stop:
                    token = None
                    try:
                        # get the next token
                        token = Scanner.get_token(fr)
                        # print the tokens to the screen
                        print("%r" % token)
                        # print the tokens to an output file
                        file_out.write("%r\n" % token)
                        # check guard condition
                        time_to_stop = token.t_type is tt.EndOfFile
                    except Scanner.IllegalCharacterError as e:
                        # Print the exception and keep going
                        print(e)
                        file_out.write(str(e))

                        # Throw away the illegal character
                        fr.get_char()
                        time_to_stop = token and token.t_type is tt.EndOfFile



    @staticmethod
    def get_token(fr):
        """
        Retrieves the next token in a file opened by a FileReader. May return a
        Comment token, which should be ignored.
        :param fr:  a FileReader object
        :return:    a Token object corresponding to the next token the
                    scanner should encounter.
                    Warning: May be a Comment token that should be ignored
        """
        assert isinstance(fr, FileReader)

        state = "Start"         # The state of the DFA
        token_string = ""       # A string that will hold the contents of the
                                # current token
        # Get the next character
        ch = fr.get_char()      # ch holds the next character

        # Skip any whitespace
        while ch and ch.isspace():
            ch = fr.get_char()

        while True:
            # Check for end of file
            if state == "Start" and fr.EOF():
                return Token(tt.EndOfFile, "End Of File")

            # If there are transitions on any character, and ch is not in the
            # list of defined transitions,
            if ANYTHING_ELSE in delta[state] and ch not in delta[state].keys():
                # make the transition
                state = delta[state][ANYTHING_ELSE]
                # save the character in the token
                token_string += ch

            # If a transition is available,
            elif ch in delta[state].keys():
                state = delta[state][ch]    # make the transition
                token_string += ch          # save the character in the token

            # If no transition is available,
            else:
                # put back the last character
                fr.put_back()

                # and make a token if we are in an accept state
                if state in token_type_for_accept_state.keys():
                    # filter out comments
                    if token_type_for_accept_state[state] in ignored_token_t:
                        state = "Start"
                        token_string = ""
                        # Skip any whitespace
                        if ch and ch.isspace():
                            while ch.isspace():
                                ch = fr.get_char()
                            # Put back the non-space character
                            fr.put_back()
                    else:
                        # determine token type from accept state
                        token_type = token_type_for_accept_state[state]

                        # filter out reserved words from identifiers
                        if token_type == tt.Identifier:
                            if token_string in keywords:
                                token_type = tt.Keyword
                            elif token_string in built_in_functions:
                                token_type = tt.BuiltInFunction

                        # return the right token
                        return Token(token_type, token_string)

                # otherwise reject the string, with an error message
                else:
                    raise Scanner.IllegalCharacterError(fr.get_line_data(), ch)
            # Get the next character
            ch = fr.get_char()



    class IllegalCharacterError(Exception):
        """
        A class used to represent exceptions that occur when the scanner
        encounters an illegal character
        """
        def __init__(self, line_data, illegal_char):
            """
            Constructor for an exception that creates an error message that
            shows what the illegal character was, the line and column number,
            the line where it occurred, and an arrow pointing to the illegal
            character.
            :param line_data:       A dictionary that holds the line number,
                                    column number, and the line
            :param illegal_char:    The illegal character
            :return:                None
            """
            super(Scanner.IllegalCharacterError, self).__init__(
                "Illegal Character %r encountered in line %d at column %d:\n"
                % (illegal_char, line_data["Line_Num"], line_data["Column"]) +
                "%s" % line_data["Line"] +
                " " * line_data["Column"] + "^\n")
