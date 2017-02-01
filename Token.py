"""
Filename: Token.py

David Dalcino
CS 6110
Prof. Reiter
Winter 2017
CSU East Bay

Scanner Assignment
Due 1/27/17


This file defines tokens and token types.
"""

from enum import Enum


class TokenType(Enum):
    """ An enumeration that defines separate identities for token types """
    EndOfFile = -1
    Integer = 1
    Float = 2
    Identifier = 3
    Comment = 4                 # these will be filtered out by the scanner
    AddOperator = 5
    SubtractOperator = 6
    MultiplyOperator = 7
    DivideOperator = 8
    ModulusOperator = 9
    OpenParen = 10
    CloseParen = 11
    OpenCurly = 12
    CloseCurly = 13
    OpenBracket = 14
    CloseBracket = 15
    Semicolon = 16
    AssignmentOperator = 17
    EqualityOperator = 18
    NotEqualOperator = 19
    LessThanOrEqualOp = 20
    LessThanOperator = 21
    Comma = 22
    String = 23
    Keyword = 24
    BuiltInFunction = 25




class Token:
    """
    A class that represents a token.
    """

    # Static database of string representations:
    lexemes = {
        TokenType.AddOperator: "+",
        TokenType.SubtractOperator: "-",
        TokenType.MultiplyOperator: "*",
        TokenType.DivideOperator: "/",
        TokenType.ModulusOperator: "%",
        TokenType.OpenParen: "(",
        TokenType.CloseParen: ")",
        TokenType.OpenCurly: "{",
        TokenType.CloseCurly: "}",
        TokenType.OpenBracket: "[",
        TokenType.CloseBracket: "]",
        TokenType.Semicolon: ";",
        TokenType.AssignmentOperator: "=",
        TokenType.EqualityOperator: "==",
        TokenType.NotEqualOperator: "!=",
        TokenType.LessThanOrEqualOp: "<=",
        TokenType.LessThanOperator: "<"
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
        """ returns a string representation of the token """
        return self.lexeme



    def __repr__(self):
        """ returns a string representation of the token """
        return "%-30s|  %s" %(str(self.t_type), self.lexeme)
