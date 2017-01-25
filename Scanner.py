# Filename: FileReader.py
# David Dalcino
# CS 6110
# Prof. Reiter
# Winter 2017
# CSU East Bay
#
# Scanner Assignment
# Due 1/27/17

from FileReader import FileReader
from Token import TokenType as tt, Token


delta = {
    # delta: a data structure that represents a delta function in a DFA. 
    # The outer dictionary's keys are states of the DFA, while the dictionaries 
    # that these keys refer to contain a list of characters to accept next, 
    # and what state to move to upon reading that character. 
    
    # The expression 'delta[current_state][character_encountered]' would 
    # resolve to the state the DFA should move into. 
    
    # Transitions to a sink state have been omitted, and may be inferred by 
    # their absence if the previous state was not an accept state.

    # Design: Some minimal amount of performance gains could be made by
    # changing the datatype of the states to an enum or integral type,
    # but I was unable to settle on a solution that I liked that was as
    # readable as this.

    "Start": {
        "0": "Int_Zero_Accept",

        "1": "Integer_Accept",          "2": "Integer_Accept",
        "3": "Integer_Accept",          "4": "Integer_Accept",
        "5": "Integer_Accept",          "6": "Integer_Accept",
        "7": "Integer_Accept",          "8": "Integer_Accept",
        "9": "Integer_Accept",

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
        ";": "Semicolon_Accept"
    },
    "Int_Zero_Accept": {
        ".": "Float_Accept",
    },
    "Integer_Accept": {
        "0": "Integer_Accept",          "1": "Integer_Accept",
        "2": "Integer_Accept",          "3": "Integer_Accept",
        "4": "Integer_Accept",          "5": "Integer_Accept",
        "6": "Integer_Accept",          "7": "Integer_Accept",
        "8": "Integer_Accept",          "9": "Integer_Accept",
        ".": "Float_Accept"
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
        "\n": "Start"
    },
    "Assignment_Accept": {
        "=": "Equals_Accept"
    },
    "Bang": {
        "=": "NotEquals_Accept"
    },
    "LessThan_Accept": {
        "=": "LessThanEquals_Accept"
    },

    # Special characters that can only be a single-character token and have
    # no valid transitions
    "Add_Accept": {},              "Subtract_Accept": {},
    "Multiply_Accept": {},         "Divide_Accept": {},
    "Modulus_Accept": {},
    "OpenParen_Accept": {},        "CloseParen_Accept": {},
    "OpenBracket_Accept": {},      "CloseBracket_Accept": {},
    "OpenCurly_Accept": {},        "CloseCurly_Accept": {},
    "Semicolon_Accept": {},
}

# Defines which token type to create for each accept state
token_for_accept_state = {
    "Int_Zero_Accept":      tt.Integer,
    "Integer_Accept":       tt.Integer,
    "Float_Accept":         tt.Float,
    "ID":                   tt.Identifier,

    "Assignment_Accept":    tt.AssignmentOperator,
    "Equals_Accept":        tt.EqualityOperator,
    "NotEquals_Accept":     tt.NotEqualOperator,
    "LessThan_Accept":      tt.LessThanOperator,
    "LessThanEquals_Accept": tt.LessThanOrEqualOperator,

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
}


class Scanner:

    def __init__(self, input_filename):
        self.filename = input_filename


    def scan_file(self):
        with FileReader(self.filename) as fr:
            token = Scanner.get_token(fr)
            print(token)

    @staticmethod
    def get_token(fr):
        assert isinstance(fr, FileReader)

        state = "Start"         # The state of the DFA
        token_string = ""       # A string that will hold the contents of the
                                # current token
        # Get the next character
        ch = fr.get_char()      # ch holds the next character

        # Skip any whitespace
        while ch.isspace():
            ch = fr.get_char()

        while True:
            # Check for end of file
            if fr.EOF():
                return Token(tt.EndOfFile, "End Of File")

            # If a transition is available,
            if ch in delta[state].keys():
                state = delta[state][ch]    # make the transition
                token_string += ch          # save the character in the token
            else:
                # If no transition is available, put back the last character
                fr.put_back()

                # and make a token if we are in an accept state
                if state in token_for_accept_state.keys():
                    return Token(token_for_accept_state[state], token_string)

                # otherwise reject the string, with an error message
                else:
                    raise Scanner.IllegalCharacterError(fr.get_line_data())
            # Get the next character
            ch = fr.get_char()



    class IllegalCharacterError(Exception):
        def __init__(self, line_data):
            super('Illegal Character encountered in line %d at column %d:\n'
                  % (line_data["Line_Num"], line_data["Column"]) +
                  '%s\n' % line_data["Line"] +
                  ' ' * line_data["Column"] + '^\n')


