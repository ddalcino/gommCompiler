"""
Filename: ParserWithST.py

David Dalcino
CS 6110
Prof. Reiter
Winter 2017
CSU East Bay

Parser With Symbol Table Assignment
Due 2/14/17


This file implements a parser, using recursive descent. All of the
recursive descent functions are generated from the grammar by another script;
the product of this script has been edited by hand to add symbol table
functionality.
"""

from Token import TokenType, Keyword, Token
from Scanner import Scanner
from FileReader import FileReader
from SymbolTable import SymbolTable, IdType
import os
#
#
# s_table = SymbolTable()

class Parser:
    """
    A static class, used to parse an input file into a parse tree.
    """
    
    
    
    @staticmethod
    def parse(filename):
        """
        Uses recursive descent to parse an input file, printing a list of
        productions as it goes. Opens the input file, and calls 'program()',
        which begins recursive descent until an EndOfFile token is reached.
        If no errors occur, it prints "Success!!!"
        :param filename:    The name of the file to parse.
        :return:            None
        """
        with FileReader(filename) as fr:
            current_token = Scanner.get_token(fr)
            Parser.program(current_token, fr)
            Parser.match(current_token, TokenType.EndOfFile, fr)
            print("\nSuccess!!!")
        
    
    
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
               isinstance(expected, TokenType))
        assert(isinstance(file_reader, FileReader))
    
        # If the current token matches the expected token, or token type,
        if current_token.equals(expected) or current_token.t_type == expected:
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
    def token_is_in(token, list_of_terminals):
        """
        Checks to see if a token is present in a list of symbols
        """
        try:
            for terminal in list_of_terminals:
                if token.equals(terminal) or token.t_type == terminal:
                    return True
            return False
        except TypeError as e:
            terminal = list_of_terminals
            return token.equals(terminal) or token.t_type == terminal
        
    
    
    @staticmethod
    def raise_error(current_token, non_terminal, file_reader):
        """
        Gets data from the file reader and formats it as an error message
        """
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
    def error_on_variable_usage(identifier, file_reader, is_decl_stmt=False):
        """
        Verifies that an identifier has been is_decl_stmt before use, and is
        currently in an open scope. If not, raises an error.
        :param identifier:      An identifier being used.
        :param file_reader:     The FileReader, used to print error data
        :param is_decl_stmt:    If False, then an error will be raised when
                                the identifier has not been declared yet or
                                is out of scope.
                                If this is True, then this function raises
                                errors when the identifier has already been
                                declared and is in scope. (use this to prevent
                                redeclaration of a variable)
        :return:                None
        """
        # if we are using the variable without having declared it earlier,
        if not is_decl_stmt and \
                s_table.find_in_all_scopes(identifier) is None:
            # report an error
            line_data = file_reader.get_line_data()
            raise Parser.Error(
                "At line %d, column %d: " % (line_data["Line_Num"],
                                             line_data["Column"]) +
                "Attempt to use undeclared variable %s.\n" % identifier +
                "%s" % line_data["Line"] +
                " " * line_data["Column"] + "^\n"
            )
        # if we are declaring the variable that has already been
        # declared in this scope,
        elif is_decl_stmt and \
                s_table.find(identifier) is not None:
            # report an error
            line_data = file_reader.get_line_data()
            raise Parser.Error(
                "At line %d, column %d: " % (line_data["Line_Num"],
                                             line_data["Column"]) +
                "Attempt to redeclare variable %s.\n" % identifier +
                "%s" % line_data["Line"] +
                " " * line_data["Column"] + "^\n"
            )

    
    
    class Error(Exception):
        """
        An error that only the Parser can raise; used by match()
        """
        pass
    
    


    @staticmethod
    def program(token, file_reader):
        """
        Implements recursive descent for the rule:
        <program> ==>
            <function_decl> <program> |
            <Epsilon>
        """
        if Parser.token_is_in(token, (Keyword.FUNC)):
            print(1, end=" ")
            Parser.function_decl(token, file_reader)
            Parser.program(token, file_reader)
        else:
            print(2, end=" ")



    @staticmethod
    def function_decl(token, file_reader):
        """
        Implements recursive descent for the rule:
        <function_decl> ==>
            Keyword.FUNC TokenType.Identifier TokenType.OpenParen <param_list>
            TokenType.CloseParen <return_identifier> <return_datatype>
            TokenType.OpenCurly <statement_list> TokenType.CloseCurly
        """
        if token.equals(Keyword.FUNC):
            print("")
            print(3, end=" ")
            Parser.match(token, Keyword.FUNC, file_reader)

            # add the function identifier to the symbol table
            function_id = token.lexeme

            # check that the identifier hasn't already been declared
            Parser.error_on_variable_usage(function_id, file_reader,
                                           is_decl_stmt=True)

            function_dict = {"type": IdType.Function}
            s_table.insert(function_id, function_dict)

            # open a new scope
            s_table.open_scope()

            Parser.match(token, TokenType.Identifier, file_reader)
            Parser.match(token, TokenType.OpenParen, file_reader)
            Parser.param_list(token, file_reader)
            Parser.match(token, TokenType.CloseParen, file_reader)

            return_val_id = token.lexeme
            Parser.return_identifier(token, file_reader)
            return_val_type = Parser.return_datatype(token, file_reader)
            function_dict["return_type"] = return_val_type
            function_dict["return_val_id"] = return_val_id

            s_table.insert(return_val_id, {"type": return_val_type})

            Parser.match(token, TokenType.OpenCurly, file_reader)
            Parser.statement_list(token, file_reader)
            Parser.match(token, TokenType.CloseCurly, file_reader)

            # close the function's scope
            s_table.close_scope()
        else:
            Parser.raise_error(token, 'function_decl', file_reader)



    @staticmethod
    def param_list(token, file_reader):
        """
        Implements recursive descent for the rule:
        <param_list> ==>
            TokenType.Identifier <datatype> <remaining_param_list> |
            <Epsilon>
        Also inserts an identifier into the symbol table
        """
        if token.t_type == TokenType.Identifier:
            print(4, end=" ")

            # get the param's identifier and datatype
            identifier = token.lexeme
            Parser.match(token, TokenType.Identifier, file_reader)
            datatype = Parser.datatype(token, file_reader)

            # check that the identifier hasn't already been declared
            Parser.error_on_variable_usage(identifier, file_reader,
                                           is_decl_stmt=True)

            # insert the identifier into the symbol table
            s_table.insert(identifier, {"type": datatype})

            Parser.remaining_param_list(token, file_reader)
        else:
            print(5, end=" ")



    @staticmethod
    def remaining_param_list(token, file_reader):
        """
        Implements recursive descent for the rule:
        <remaining_param_list> ==>
            TokenType.Comma TokenType.Identifier <datatype>
            <remaining_param_list> |
            <Epsilon>
        """
        if token.t_type == TokenType.Comma:
            print(6, end=" ")
            Parser.match(token, TokenType.Comma, file_reader)

            # get the param's identifier and datatype
            identifier = token.lexeme
            Parser.match(token, TokenType.Identifier, file_reader)
            datatype = Parser.datatype(token, file_reader)

            # check that the identifier hasn't already been declared
            Parser.error_on_variable_usage(identifier, file_reader,
                                           is_decl_stmt=True)

            # insert the identifier into the symbol table
            s_table.insert(identifier, {"type": datatype})

            Parser.remaining_param_list(token, file_reader)
        else:
            print(7, end=" ")



    @staticmethod
    def datatype(token, file_reader):
        """
        Implements recursive descent for the rule:
        <datatype> ==>
            Keyword.INT |
            Keyword.FLOAT |
            Keyword.CHAR |
            TokenType.OpenBracket TokenType.Integer TokenType.CloseBracket
            <array_of_datatype>
        :return:    The datatype, as a SymbolTable.IdType enum
        """
        if token.equals(Keyword.INT):
            print(8, end=" ")
            Parser.match(token, Keyword.INT, file_reader)
            return IdType.Integer
        elif token.equals(Keyword.FLOAT):
            print(9, end=" ")
            Parser.match(token, Keyword.FLOAT, file_reader)
            return IdType.Float
        elif token.equals(Keyword.CHAR):
            print(10, end=" ")
            Parser.match(token, Keyword.CHAR, file_reader)
            return IdType.Char
        elif token.t_type == TokenType.OpenBracket:
            print(11, end=" ")
            Parser.match(token, TokenType.OpenBracket, file_reader)
            Parser.match(token, TokenType.Integer, file_reader)
            Parser.match(token, TokenType.CloseBracket, file_reader)
            return Parser.array_of_datatype(token, file_reader)
        else:
            Parser.raise_error(token, 'datatype', file_reader)



    @staticmethod
    def array_of_datatype(token, file_reader):
        """
        Implements recursive descent for the rule:
        <array_of_datatype> ==>
            Keyword.INT |
            Keyword.FLOAT |
            Keyword.CHAR
        :return:    The datatype, as a SymbolTable.IdType enum
        """
        if token.equals(Keyword.INT):
            print(12, end=" ")
            Parser.match(token, Keyword.INT, file_reader)
            return IdType.ArrayInteger
        elif token.equals(Keyword.FLOAT):
            print(13, end=" ")
            Parser.match(token, Keyword.FLOAT, file_reader)
            return  IdType.ArrayFloat
        elif token.equals(Keyword.CHAR):
            print(14, end=" ")
            Parser.match(token, Keyword.CHAR, file_reader)
            return IdType.ArrayChar
        else:
            Parser.raise_error(token, 'array_of_datatype', file_reader)



    @staticmethod
    def return_identifier(token, file_reader):
        """
        Implements recursive descent for the rule:
        <return_identifier> ==>
            TokenType.Identifier
        """
        if token.t_type == TokenType.Identifier:
            print(15, end=" ")
            Parser.match(token, TokenType.Identifier, file_reader)
        else:
            Parser.raise_error(token, 'return_identifier', file_reader)



    @staticmethod
    def return_datatype(token, file_reader):
        """
        Implements recursive descent for the rule:
        <return_datatype> ==>
            <datatype>
        :return:    The datatype, as a SymbolTable.IdType enum
        """
        if Parser.token_is_in(token, (Keyword.INT, Keyword.FLOAT, Keyword.CHAR,
                                      TokenType.OpenBracket)):
            print(16, end=" ")
            return Parser.datatype(token, file_reader)
        else:
            Parser.raise_error(token, 'return_datatype', file_reader)



    @staticmethod
    def statement_list(token, file_reader):
        """
        Implements recursive descent for the rule:
        <statement_list> ==>
            <basic_statement> <statement_list> |
            <Epsilon>
        """
        if Parser.token_is_in(token, (Keyword.RETURN, Keyword.IF, Keyword.WHILE,
                                      Keyword.VAR, TokenType.Identifier)):
            print("")
            print(17, end=" ")
            Parser.basic_statement(token, file_reader)
            Parser.statement_list(token, file_reader)
        else:
            print(18, end=" ")



    @staticmethod
    def basic_statement(token, file_reader):
        """
        Implements recursive descent for the rule:
        <basic_statement> ==>
            Keyword.RETURN TokenType.Semicolon |
            Keyword.IF <remaining_if_statement> |
            Keyword.WHILE <remaining_while_statement> |
            Keyword.VAR TokenType.Identifier <datatype> TokenType.Semicolon |
            TokenType.Identifier <assignment_or_function_call>
            TokenType.Semicolon
        """
        if token.equals(Keyword.RETURN):
            print(19, end=" ")
            Parser.match(token, Keyword.RETURN, file_reader)
            Parser.match(token, TokenType.Semicolon, file_reader)
        elif token.equals(Keyword.IF):
            print(20, end=" ")
            Parser.match(token, Keyword.IF, file_reader)
            Parser.remaining_if_statement(token, file_reader)
        elif token.equals(Keyword.WHILE):
            print(21, end=" ")
            Parser.match(token, Keyword.WHILE, file_reader)
            Parser.remaining_while_statement(token, file_reader)
        elif token.equals(Keyword.VAR):
            print(22, end=" ")
            Parser.match(token, Keyword.VAR, file_reader)

            # get the param's identifier and datatype
            identifier = token.lexeme
            Parser.match(token, TokenType.Identifier, file_reader)
            datatype = Parser.datatype(token, file_reader)

            # check that the identifier hasn't already been declared
            Parser.error_on_variable_usage(identifier, file_reader, True)

            # insert the identifier into the symbol table
            s_table.insert(identifier, {"type": datatype})

            Parser.match(token, TokenType.Semicolon, file_reader)
        elif token.t_type == TokenType.Identifier:
            print(23, end=" ")

            # get the param's identifier and look it up
            identifier = token.lexeme
            Parser.error_on_variable_usage(identifier, file_reader)

            Parser.match(token, TokenType.Identifier, file_reader)
            Parser.assignment_or_function_call(token, file_reader)
            Parser.match(token, TokenType.Semicolon, file_reader)
        else:
            Parser.raise_error(token, 'basic_statement', file_reader)



    @staticmethod
    def assignment_or_function_call(token, file_reader):
        """
        Implements recursive descent for the rule:
        <assignment_or_function_call> ==>
            TokenType.AssignmentOperator <expression> |
            TokenType.OpenBracket <expression> TokenType.CloseBracket
            TokenType.AssignmentOperator <expression> |
            TokenType.OpenParen <expression_list> TokenType.CloseParen
        """
        if token.t_type == TokenType.AssignmentOperator:
            print(24, end=" ")
            Parser.match(token, TokenType.AssignmentOperator, file_reader)
            Parser.expression(token, file_reader)
        elif token.t_type == TokenType.OpenBracket:
            print(25, end=" ")
            Parser.match(token, TokenType.OpenBracket, file_reader)
            Parser.expression(token, file_reader)
            Parser.match(token, TokenType.CloseBracket, file_reader)
            Parser.match(token, TokenType.AssignmentOperator, file_reader)
            Parser.expression(token, file_reader)
        elif token.t_type == TokenType.OpenParen:
            print(26, end=" ")
            Parser.match(token, TokenType.OpenParen, file_reader)
            Parser.expression_list(token, file_reader)
            Parser.match(token, TokenType.CloseParen, file_reader)
        else:
            Parser.raise_error(token, 'assignment_or_function_call',
                               file_reader)



    @staticmethod
    def expression_list(token, file_reader):
        """
        Implements recursive descent for the rule:
        <expression_list> ==>
            <expression> <remaining_expression_list> |
            <Epsilon>
        """
        if Parser.token_is_in(token, (TokenType.OpenParen, TokenType.Identifier,
                TokenType.Float, TokenType.Integer, TokenType.String)):
            print(27, end=" ")
            Parser.expression(token, file_reader)
            Parser.remaining_expression_list(token, file_reader)
        else:
            print(28, end=" ")



    @staticmethod
    def remaining_expression_list(token, file_reader):
        """
        Implements recursive descent for the rule:
        <remaining_expression_list> ==>
            TokenType.Comma <expression> <remaining_expression_list> |
            <Epsilon>
        """
        if token.t_type == TokenType.Comma:
            print(29, end=" ")
            Parser.match(token, TokenType.Comma, file_reader)
            Parser.expression(token, file_reader)
            Parser.remaining_expression_list(token, file_reader)
        else:
            print(30, end=" ")



    @staticmethod
    def remaining_if_statement(token, file_reader):
        """
        Implements recursive descent for the rule:
        <remaining_if_statement> ==>
            TokenType.OpenParen <boolean_expression> TokenType.CloseParen
            TokenType.OpenCurly <statement_list> TokenType.CloseCurly
            <else_clause>
        """
        if token.t_type == TokenType.OpenParen:
            print(31, end=" ")
            Parser.match(token, TokenType.OpenParen, file_reader)
            Parser.boolean_expression(token, file_reader)
            Parser.match(token, TokenType.CloseParen, file_reader)
            Parser.match(token, TokenType.OpenCurly, file_reader)

            s_table.open_scope()
            Parser.statement_list(token, file_reader)
            s_table.close_scope()

            Parser.match(token, TokenType.CloseCurly, file_reader)
            Parser.else_clause(token, file_reader)
        else:
            Parser.raise_error(token, 'remaining_if_statement', file_reader)



    @staticmethod
    def else_clause(token, file_reader):
        """
        Implements recursive descent for the rule:
        <else_clause> ==>
            Keyword.ELSE TokenType.OpenCurly <statement_list>
            TokenType.CloseCurly |
            <Epsilon>
        """
        if token.equals(Keyword.ELSE):
            print(32, end=" ")
            Parser.match(token, Keyword.ELSE, file_reader)
            Parser.match(token, TokenType.OpenCurly, file_reader)

            s_table.open_scope()
            Parser.statement_list(token, file_reader)
            s_table.close_scope()

            Parser.match(token, TokenType.CloseCurly, file_reader)
        else:
            print(33, end=" ")



    @staticmethod
    def remaining_while_statement(token, file_reader):
        """
        Implements recursive descent for the rule:
        <remaining_while_statement> ==>
            TokenType.OpenParen <boolean_expression> TokenType.CloseParen
            TokenType.OpenCurly <statement_list> TokenType.CloseCurly
        """
        if token.t_type == TokenType.OpenParen:
            print(34, end=" ")
            Parser.match(token, TokenType.OpenParen, file_reader)
            Parser.boolean_expression(token, file_reader)
            Parser.match(token, TokenType.CloseParen, file_reader)
            Parser.match(token, TokenType.OpenCurly, file_reader)

            s_table.open_scope()
            Parser.statement_list(token, file_reader)
            s_table.close_scope()

            Parser.match(token, TokenType.CloseCurly, file_reader)
        else:
            Parser.raise_error(token, 'remaining_while_statement', file_reader)



    @staticmethod
    def expression(token, file_reader):
        """
        Implements recursive descent for the rule:
        <expression> ==>
            <term> <expr_prime>
        """
        if Parser.token_is_in(token, (TokenType.OpenParen, TokenType.Identifier,
                TokenType.Float, TokenType.Integer, TokenType.String)):
            print(35, end=" ")
            Parser.term(token, file_reader)
            Parser.expr_prime(token, file_reader)
        else:
            Parser.raise_error(token, 'expression', file_reader)



    @staticmethod
    def expr_prime(token, file_reader):
        """
        Implements recursive descent for the rule:
        <expr_prime> ==>
            TokenType.AddOperator <term> <expr_prime> |
            TokenType.SubtractOperator <term> <expr_prime> |
            <Epsilon>
        """
        if token.t_type == TokenType.AddOperator:
            print(36, end=" ")
            Parser.match(token, TokenType.AddOperator, file_reader)
            Parser.term(token, file_reader)
            Parser.expr_prime(token, file_reader)
        elif token.t_type == TokenType.SubtractOperator:
            print(37, end=" ")
            Parser.match(token, TokenType.SubtractOperator, file_reader)
            Parser.term(token, file_reader)
            Parser.expr_prime(token, file_reader)
        else:
            print(38, end=" ")



    @staticmethod
    def term(token, file_reader):
        """
        Implements recursive descent for the rule:
        <term> ==>
            <factor> <term_prime>
        """
        if Parser.token_is_in(token, (TokenType.OpenParen, TokenType.Identifier,
                TokenType.Float, TokenType.Integer, TokenType.String)):
            print(39, end=" ")
            Parser.factor(token, file_reader)
            Parser.term_prime(token, file_reader)
        else:
            Parser.raise_error(token, 'term', file_reader)



    @staticmethod
    def term_prime(token, file_reader):
        """
        Implements recursive descent for the rule:
        <term_prime> ==>
            TokenType.MultiplyOperator <factor> <term_prime> |
            TokenType.DivideOperator <factor> <term_prime> |
            TokenType.ModulusOperator <factor> <term_prime> |
            <Epsilon>
        """
        if token.t_type == TokenType.MultiplyOperator:
            print(40, end=" ")
            Parser.match(token, TokenType.MultiplyOperator, file_reader)
            Parser.factor(token, file_reader)
            Parser.term_prime(token, file_reader)
        elif token.t_type == TokenType.DivideOperator:
            print(41, end=" ")
            Parser.match(token, TokenType.DivideOperator, file_reader)
            Parser.factor(token, file_reader)
            Parser.term_prime(token, file_reader)
        elif token.t_type == TokenType.ModulusOperator:
            print(42, end=" ")
            Parser.match(token, TokenType.ModulusOperator, file_reader)
            Parser.factor(token, file_reader)
            Parser.term_prime(token, file_reader)
        else:
            print(43, end=" ")



    @staticmethod
    def factor(token, file_reader):
        """
        Implements recursive descent for the rule:
        <factor> ==>
            TokenType.OpenParen <expression> TokenType.CloseParen |
            TokenType.Identifier <variable_or_function_call> |
            TokenType.Float |
            TokenType.Integer |
            TokenType.String
        """
        if token.t_type == TokenType.OpenParen:
            print(44, end=" ")
            Parser.match(token, TokenType.OpenParen, file_reader)
            Parser.expression(token, file_reader)
            Parser.match(token, TokenType.CloseParen, file_reader)
        elif token.t_type == TokenType.Identifier:
            print(45, end=" ")

            # Check to be sure that it has been declared in an open scope
            Parser.error_on_variable_usage(token.lexeme, file_reader)

            Parser.match(token, TokenType.Identifier, file_reader)
            Parser.variable_or_function_call(token, file_reader)
        elif token.t_type == TokenType.Float:
            print(46, end=" ")
            Parser.match(token, TokenType.Float, file_reader)
        elif token.t_type == TokenType.Integer:
            print(47, end=" ")
            Parser.match(token, TokenType.Integer, file_reader)
        elif token.t_type == TokenType.String:
            print(48, end=" ")
            Parser.match(token, TokenType.String, file_reader)
        else:
            Parser.raise_error(token, 'factor', file_reader)



    @staticmethod
    def variable_or_function_call(token, file_reader):
        """
        Implements recursive descent for the rule:
        <variable_or_function_call> ==>
            TokenType.OpenBracket <expression> TokenType.CloseBracket |
            TokenType.OpenParen <expression_list> TokenType.CloseParen |
            <Epsilon>
        """
        if token.t_type == TokenType.OpenBracket:
            print(49, end=" ")
            Parser.match(token, TokenType.OpenBracket, file_reader)
            Parser.expression(token, file_reader)
            Parser.match(token, TokenType.CloseBracket, file_reader)
        elif token.t_type == TokenType.OpenParen:
            print(50, end=" ")
            Parser.match(token, TokenType.OpenParen, file_reader)
            Parser.expression_list(token, file_reader)
            Parser.match(token, TokenType.CloseParen, file_reader)
        else:
            print(51, end=" ")



    @staticmethod
    def boolean_expression(token, file_reader):
        """
        Implements recursive descent for the rule:
        <boolean_expression> ==>
            <expression> <boolean_comparator> <expression>
        """
        if Parser.token_is_in(token, (TokenType.OpenParen, TokenType.Identifier,
                TokenType.Float, TokenType.Integer, TokenType.String)):
            print(52, end=" ")
            Parser.expression(token, file_reader)
            Parser.boolean_comparator(token, file_reader)
            Parser.expression(token, file_reader)
        else:
            Parser.raise_error(token, 'boolean_expression', file_reader)



    @staticmethod
    def boolean_comparator(token, file_reader):
        """
        Implements recursive descent for the rule:
        <boolean_comparator> ==>
            TokenType.EqualityOperator |
            TokenType.NotEqualOperator |
            TokenType.LessThanOperator |
            TokenType.LessThanOrEqualOp
        """
        if token.t_type == TokenType.EqualityOperator:
            print(53, end=" ")
            Parser.match(token, TokenType.EqualityOperator, file_reader)
        elif token.t_type == TokenType.NotEqualOperator:
            print(54, end=" ")
            Parser.match(token, TokenType.NotEqualOperator, file_reader)
        elif token.t_type == TokenType.LessThanOperator:
            print(55, end=" ")
            Parser.match(token, TokenType.LessThanOperator, file_reader)
        elif token.t_type == TokenType.LessThanOrEqualOp:
            print(56, end=" ")
            Parser.match(token, TokenType.LessThanOrEqualOp, file_reader)
        else:
            Parser.raise_error(token, 'boolean_comparator', file_reader)



test_file_dir = "/home/dave/PycharmProjects/Compiler/testParserST/"

if __name__ == "__main__":
    # For every file in the test file directory,
    for f in os.listdir(test_file_dir):

        # Prepend the path of the test file directory
        input_filename = test_file_dir + f

        print("\nParsing file " + f)

        s_table = SymbolTable()

        # Parser.parse(input_filename)

        try:
            Parser.parse(input_filename)
        except Exception as ex:
            print("\nException occurred while parsing file %s:\n%s" % (f, ex))

        s_table.display()
