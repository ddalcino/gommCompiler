"""
Filename: Token.py
Tested using Python 3.5.1

David Dalcino
CS 6110
Prof. Reiter
Winter 2017
CSU East Bay

Scanner Assignment Due 1/27/17
Changed slightly for the Parser assignment, due 2/9/17
Changed again for final project, due 3/9/17

This file defines tokens and token types.
"""

from enum import Enum


class TokenType(Enum):
    """ An enumeration that defines separate identities for token types """
    EndOfFile = -1
    Integer = 1
    Float = 2
    Char = 3
    Identifier = 4
    Comment = 5                 # these will be filtered out by the scanner
    AddSubOperator = 6
    MulDivModOperator = 7
    OpenParen = 10
    CloseParen = 11
    OpenCurly = 12
    CloseCurly = 13
    OpenBracket = 14
    CloseBracket = 15
    Semicolon = 16
    AssignmentOperator = 17
    RelationalOperator = 18
    Comma = 22
    String = 23
    KeywordIf = 24
    KeywordElse = 25
    KeywordWhile = 26
    KeywordFunc = 27
    KeywordReturn = 28
    KeywordInt = 29
    KeywordFloat = 30
    KeywordChar = 31
    KeywordVar = 32
    KeywordBool = 33
    KeywordProto = 34


class Token:
    """
    A class that represents a token.
    """

    # Static database of string representations:
    lexemes = {
        TokenType.OpenParen: "(",
        TokenType.CloseParen: ")",
        TokenType.OpenCurly: "{",
        TokenType.CloseCurly: "}",
        TokenType.OpenBracket: "[",
        TokenType.CloseBracket: "]",
        TokenType.Semicolon: ";",
        TokenType.AssignmentOperator: "=",
        # TokenType.KeywordBool: "bool",    # Bools are for internal use only
        TokenType.KeywordChar: "char",
        TokenType.KeywordElse: "else",
        TokenType.KeywordFloat: "float",
        TokenType.KeywordFunc: "func",
        TokenType.KeywordIf: "if",
        TokenType.KeywordInt: "int",
        TokenType.KeywordReturn: "return",
        TokenType.KeywordVar: "var",
        TokenType.KeywordWhile: "while",
        TokenType.KeywordProto: "proto",
    }


    # Static translation table from lexeme to keyword
    keywords = {
        "char":     TokenType.KeywordChar,
        "else":     TokenType.KeywordElse,
        "float":    TokenType.KeywordFloat,
        "func":     TokenType.KeywordFunc,
        "if":       TokenType.KeywordIf,
        "int":      TokenType.KeywordInt,
        "proto":    TokenType.KeywordProto,
        "return":   TokenType.KeywordReturn,
        "var":      TokenType.KeywordVar,
        "while":    TokenType.KeywordWhile,
        # Not yet implemented; bools are currently for internal use only,
        # for conditional expressions
        # "bool":     TokenType.KeywordBool,
    }



    def __init__(self, token_type, lexeme):
        """
        Initializes a Token
        :param token_type:  a TokenType object
        :param lexeme:      a string; the token as a lexeme
        :return:            None
        """

        # Disallow clients to use non-TokenType objects
        assert isinstance(token_type, TokenType)

        # The type of token, a TokenType enum
        self.t_type = token_type

        # self.lexeme = The string representation of the token
        # If the string representation is in the static database str_repr,
        # we can point to that location instead of using excess memory
        if token_type in Token.lexemes.keys():
            self.lexeme = Token.lexemes[token_type]
        else:
            self.lexeme = lexeme



    def __str__(self):
        """ returns a string representation of the token's lexeme """
        return self.lexeme



    def __repr__(self):
        """ returns a string representation of the token """
        return "<%s, lex=%s>" %(str(self.t_type), self.lexeme)



    def assignTo(self, other_token):
        """
        Copies the data in other_token into this token
        :param other_token:     The other token, from which to copy data
        :return:                None
        """
        assert isinstance(other_token, Token)

        self.t_type = other_token.t_type
        self.lexeme = other_token.lexeme



    def equals(self, other_token):
        """
        Determines equivalence of two Tokens
        :param other_token:     The token to compare to self
        :return:                True if the tokens are equal, otherwise False
        """
        return isinstance(other_token, Token) and\
            self.t_type == other_token.t_type and \
            self.lexeme == other_token.lexeme

