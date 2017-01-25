from enum import Enum


class TokenType(Enum):
    EndOfFile = -1
    Integer = 1
    Float = 2
    Identifier = 3
    # Comment = 4             # oops, not a token
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
    LessThanOrEqualOperator = 20
    LessThanOperator = 21



class Token:
    """
    A class that represents a token.
    """

    # Static database of string representations:
    str_repr = {
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
        TokenType.LessThanOrEqualOperator: "<=",
        TokenType.LessThanOperator: "<"
    }



    def __init__(self, token_type, string_repr):
        """
        Initializes a Token
        :param token_type:  a TokenType object
        :param string_repr: a string representation of the token
        :return:            None
        """

        # Disallow clients to use non-TokenType objects
        assert isinstance(token_type, TokenType)

        self.t_type = token_type        # The type of token, a TokenType enum

        # self.string_repr = The string representation of the token
        # If the string representation is in the static database str_repr,
        # we can point to that location instead of reserving more memory
        if token_type in Token.str_repr.keys():
            self.string_repr = Token.str_repr[token_type]
        else:
            self.string_repr = string_repr



    def __str__(self):
        """ returns a string representation of the token """
        return self.string_repr



    def __repr__(self):
        """ returns a string representation of the token """
        return self.string_repr
