"""
Filename: Parser.py

David Dalcino
CS 6110
Prof. Reiter
Winter 2017
CSU East Bay

Parser Assignment
Due 2/9/17


This file implements a parser, using recursive descent. I didn't like the
idea of hand-coding a different function for each non-terminal symbol in my
grammar (right now, there are 24 non-terminals in my grammar), so I fit the
whole grammar into a data structure, and I wrote one recursive descent
function that reads from that data structure to determine what the rules of
the language are. This also has the effect that the grammar definition can be
easily read and checked, and changes to the grammar will change the behavior
of the code without rewriting any functions.

To simplify the parser, if there is a production in a particular list of
productions that begins with a non-terminal symbol, then that is the
only production in the list that can begin with that non-terminal symbol.
This way, the parser doesn't have to choose between non-terminal symbols; it
can just assume that the first production that begins with a non-terminal
symbol will work.
"""

from Token import TokenType as tt, Keyword, Token
from Scanner import Scanner
from FileReader import FileReader


grammar = {
    # grammar: a data structure that represents a complete grammar. The outer
    # structure is a dictionary; its keys represent non-terminal symbols,
    # and the values associated with those keys are a list of productions.

    # Each production is a list, in the form (non-terminal|terminal)+
    # A production could also be a None object instead of a list; this
    # designates an epsilon.

    # Each non-terminal symbol in a production is a string, which is the name
    # of that symbol.
    # Each terminal in a production is either a Token or a Token.TokenType
    # object. This is done to differentiate between different keywords;
    # conceivably, I could change every instance of a keyword into the
    # TokenType for a keyword, but I think that makes the grammar a lot less
    # useful and harder to read. Alternately, I could change each keyword
    # into its own TokenType

    # A program is a list of function declarations
    "program": (
        ("function_decl", "program",),
        None,
    ),

    # A function declaration looks like:
    # func <id> (<param_list>) <ret_identifier> <ret_datatype> {<code_block>}
    "function_decl": (
        (Keyword.FUNC, tt.Identifier, tt.OpenParen, "param_list",
         tt.CloseParen, "return_identifier", "return_datatype", tt.OpenCurly,
         "statement_list", tt.CloseCurly,),
    ),

    # A parameter list is a list of basic declaration statements, of the form
    #  <identifier> <datatype>
    "param_list": (
        (tt.Identifier, "datatype", "remaining_param_list",),
        None,
    ),

    "remaining_param_list": (
        (tt.Comma, tt.Identifier, "datatype", "remaining_param_list",),
        None,        # an epsilon
    ),

    "datatype": (
        (Keyword.INT,),
        (Keyword.FLOAT,),
        (Keyword.CHAR,),
        (tt.OpenBracket, tt.Integer, tt.CloseBracket, "array_of_datatype",),
    ),

    "array_of_datatype": (
        (Keyword.INT,),
        (Keyword.FLOAT,),
        (Keyword.CHAR,),
    ),

    "return_identifier": (
        (tt.Identifier,),
    ),

    "return_datatype": (
        ("datatype",),
    ),

    # A statement list is a list of statements
    "statement_list": (
        ("basic_statement", "statement_list"),
        None,
    ),

    # A basic statement is in the form:
    # <statement> ::= <return_statement> | <if_statement> | <loop_statement> |
    # <declaration_statement> | <assignment_statement> |
    "basic_statement": (
        (Keyword.RETURN, tt.Semicolon),                 # return statement
        (Keyword.IF, "remaining_if_statement"),         # if statement
        (Keyword.WHILE, "remaining_while_statement"),   # loop statement
        # variable declaration statement
        (Keyword.VAR, tt.Identifier, "datatype", tt.Semicolon),
        # assignment or function call
        (tt.Identifier, "assignment_or_function_call", tt.Semicolon),
    ),

    "assignment_or_function_call": (
        (tt.AssignmentOperator, "expression"),          # assignment statement
        (tt.OpenBracket, "expression", tt.CloseBracket,     # array indexing
         tt.AssignmentOperator, "expression"),          # assignment statement
        (tt.OpenParen, "expression_list", tt.CloseParen),   # function call
    ),

    "expression_list": (
        ("expression", "remaining_expression_list"),
        None,
    ),
    "remaining_expression_list": (
        (tt.Comma, "expression", "remaining_expression_list",),
        None,
    ),

    "remaining_if_statement": (
        (tt.OpenParen, "boolean_expression", tt.CloseParen,
         tt.OpenCurly, "statement_list", tt.CloseCurly, "else_clause"),
    ),
    "else_clause": (
        (Keyword.ELSE, tt.OpenCurly, "statement_list", tt.CloseCurly,),
        None,
    ),

    "remaining_while_statement": (
        (tt.OpenParen, "boolean_expression", tt.CloseParen,
         tt.OpenCurly, "statement_list", tt.CloseCurly,),
    ),

    "expression": (
        ("term", "expr_prime"),
    ),
    "expr_prime": (
        (tt.AddOperator, "term", "expr_prime",),
        (tt.SubtractOperator, "term", "expr_prime",),
        None
    ),
    "term": (
        ("factor", "term_prime"),
    ),
    "term_prime": (
        (tt.MultiplyOperator, "factor", "term_prime"),
        (tt.DivideOperator, "factor", "term_prime"),
        (tt.ModulusOperator, "factor", "term_prime"),
        None
    ),
    "factor": (
        (tt.OpenParen, "expression", tt.CloseParen),
        (tt.Identifier, "variable_or_function_call"),
        (tt.Float,),
        (tt.Integer,),
        (tt.String,),
    ),
    "variable_or_function_call": (
        (tt.OpenBracket, "expression", tt.CloseBracket),    # array indexing
        (tt.OpenParen, "expression_list", tt.CloseParen),   # function call
        None                            # epsilon, for variable
    ),

    "boolean_expression": (
        ("expression", "boolean_comparator", "expression",),
    ),
    "boolean_comparator": (
        (tt.EqualityOperator,),
        (tt.NotEqualOperator,),
        (tt.LessThanOperator,),
        (tt.LessThanOrEqualOp,),
    ),
}


class Parser:
    """
    A static class, used to parse an input file into a parse tree.
    """

    @staticmethod
    def parse(filename):
        """
        Uses recursive descent to parse an input file, printing a list of
        productions as it goes. Opens the input file, starts off with the
        non-terminal symbol 'program', and calls rd_parse(), which calls
        itself recursively until an EndOfFile token is reached. If no errors
        occur, it prints "Success!!!"
        :param filename:    The name of the file to parse.
        :return:            None
        """
        with FileReader(filename) as fr:
            current_token = Scanner.get_token(fr)
            non_terminal = "program"
            Parser.rd_parse(non_terminal, current_token, fr)
            Parser.match(current_token, tt.EndOfFile, fr)
            print("Success!!!")



    @staticmethod
    def rd_parse(non_terminal, current_token, file_reader):
        """
        Uses recursive descent to parse an input file, printing a list of
        productions as it goes. Reads the rules of the language from the
        'grammar' data structure.
        :param non_terminal:    The current non-terminal symbol
        :param current_token:   The current token being read. It is passed by
                                reference, and will be modified each time the
                                function is called.
        :param file_reader:     The FileReader from which to read the next token
        :return:
        """
        assert(non_terminal in grammar.keys())
        assert(isinstance(current_token, Token))

        # First, choose a production, based on what's in grammar[non_terminal]
        if None in grammar[non_terminal]:
            # there's an epsilon move available, so we should check if
            # current_token exists in the set of first terminals for
            # non_terminal; if not, we should take the epsilon move
            if not Parser.is_in_first_terminals(current_token, non_terminal):
                # take the epsilon move
                # report which production we are using ...
                print("%s %d" %
                      (non_terminal, grammar[non_terminal].index(None)))
                return

        # If we didn't take the epsilon move, then check current_token
        # against the first terminal in each production
        for i in range(len(grammar[non_terminal])):
            production = grammar[non_terminal][i]
            if production is not None:              # not an epsilon move
                # get the first symbol in the production
                first = production[0]

                # if current_token fits into first, then choose is production:
                if Parser.fits(current_token, first):
                    # report which production we are using ...
                    print("%s %d" % (non_terminal, i))
                    # ... and use that production
                    for symbol in production:
                        # if it's a non-terminal symbol,
                        if isinstance(symbol, str):
                            Parser.rd_parse(symbol, current_token, file_reader)
                        else:
                            # otherwise match the symbol and move on
                            Parser.match(current_token, symbol, file_reader)
                    # return gracefully
                    return

        # At this point, if we have not returned, it is because we could not
        # find a production that matches the current token
        line_data = file_reader.get_line_data()
        raise Parser.Error(
            "At line %d, column %d: " % (line_data["Line_Num"],
                                         line_data["Column"]) +
            "Could not find a production for terminal %r in non-terminal %s" %
            (current_token, non_terminal) +
            "\n%s" % line_data["Line"] +
            " " * line_data["Column"] + "^\n"
        )



    @staticmethod
    def match(current_token, expected, file_reader):
        """
        Matches the current token with an expected token or token type,
        then reads the next token from the scanner.
        If a match cannot be made, raises a Parser.Error object.
        :param current_token:   The current token being read
        :param expected:        Either an expected Token (in the case of a
                                particular keyword) or a TokenType
        :param file_reader:     The FileReader from which to read the next token
        :return:                None
        """
        assert(isinstance(current_token, Token))
        assert(isinstance(expected, Token) or
               isinstance(expected, tt))
        assert(isinstance(file_reader, FileReader))

        # If the current token matches the expected token, or token type,
        if current_token.equals(expected) or \
                current_token.t_type == expected:
            # then get the next token and put it in current_token
            current_token.assignTo(Scanner.get_token(file_reader))
        else:
            # otherwise, we have an error.
            line_data = file_reader.get_line_data()
            raise Parser.Error(
                "At line %d, column %d: " % (line_data["Line_Num"],
                                             line_data["Column"]) +
                "Tried to match %r with %r, but they were unequal.\n" %
                (current_token, expected) +
                "%s" % line_data["Line"] +
                " " * line_data["Column"] + "^\n"
            )



    @staticmethod
    def first_terminals(non_terminal, skip_epsilon=True):
        """
        Returns a list of Token or TokenTypes that represent terminal
        symbols, which are the set of all terminal symbols that can begin a
        sentence derived from the parameter non-terminal symbol.
        :param non_terminal:    The non-terminal symbol for which we are
                                retrieving a set of first terminals
        :param skip_epsilon:    If True, the function will omit epsilon from
                                the list of returned terminal symbols;
                                otherwise it adds a None object if an epsilon
                                is encountered
        :return:                the set of all terminal symbols that can begin a
                                sentence derived from non_terminal
        """
        first = []
        for production in grammar[non_terminal]:
            if production is not None:
                # if the first symbol in the production is a non-terminal,
                if isinstance(production[0], str):
                    # add all non-terminals for the production to first
                    first.extend(Parser.first_terminals(production[0]))
                else:
                    # otherwise, add a terminal symbol
                    first.append(production[0])
            elif not skip_epsilon:
                # The list of productions includes an epsilon, so add a None
                # to the list
                first.append(None)
        return first



    @staticmethod
    def is_in_first_terminals(token, non_terminal):
        """
        Checks to see if a token is in the set of terminal symbols that can
        begin a sentence derived from a non-terminal symbol.
        :param token:           The token to check
        :param non_terminal:    The non-terminal symbol that may or may not
                                produce a terminal that matches token
        :return:                True if the token can be produced by the
                                non-terminal symbol; otherwise False
        """
        for terminal in Parser.first_terminals(non_terminal):
            if token.equals(terminal) or token.t_type == terminal:
                return True
        return False



    @staticmethod
    def fits(token, terminal_or_non_terminal):
        """
        Determines whether a token fits a terminal or non-terminal symbol.
        If terminal_or_non_terminal is a terminal, this function
        checks whether or not the token is a match for that terminal.
        If terminal_or_non_terminal is a non-terminal, this function checks
        the token against the set of terminal symbols that can
        begin a sentence derived from the non-terminal symbol.
        :param token:                       the token to evaluate
        :param terminal_or_non_terminal:    a terminal or non-terminal symbol
        :return:        True if the token can be matched to the parameter
                        terminal_or_non_terminal, or false if it cannot
        """
        assert(isinstance(token, Token))

        if isinstance(terminal_or_non_terminal, str):
            # it's a non-terminal
            non_terminal = terminal_or_non_terminal

            # Note: Given the way the grammar is written, this check should
            # be unnecessary, and we should just return True: if we have
            # reached a non-terminal symbol, it should be the only one
            # available to us, and we should just start using that production;
            # if it doesn't work, we'll get an error anyway. However, this
            # implementation leaves open the possibility of writing a grammar
            # that has multiple productions that begin with non-terminal
            # symbols, as long as FIRST(non_terminal) is disjoint with
            # FIRST(all other non_terminal symbols)
            return Parser.is_in_first_terminals(token, non_terminal)
        else:
            # it's a terminal, which is either a Token or a TokenType
            terminal = terminal_or_non_terminal
            return token.equals(terminal) or token.t_type == terminal


    class Error(Exception):
        """ An error that only the Parser can raise; used by Parser.match() """
        pass

