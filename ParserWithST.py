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

The grammar implemented is summarized here:
<program> ==>
    1 <function_decl> {<function_decl>} |
    2 <Epsilon>
<function_decl> ==>
    3 TokenType.KeywordFunc TokenType.Identifier TokenType.OpenParen <param_list>
        TokenType.CloseParen <return_identifier> <return_datatype>
        TokenType.OpenCurly <statement_list> TokenType.CloseCurly
<param_list> ==>
    4 TokenType.Identifier <datatype>
        {TokenType.Comma TokenType.Identifier <datatype>}  |
    5 <Epsilon>
<datatype> ==>
    8 TokenType.KeywordInt |
    9 TokenType.KeywordFloat |
    10 TokenType.KeywordChar |
    11 TokenType.OpenBracket TokenType.Integer TokenType.CloseBracket
        <array_of_datatype>
<array_of_datatype> ==>
    12 TokenType.KeywordInt |
    13 TokenType.KeywordFloat |
    14 TokenType.KeywordChar
<return_identifier> ==>
    15 TokenType.Identifier
<return_datatype> ==>
    16 <datatype>
<statement_list> ==>
    17 <basic_statement> {<basic_statement>} |
    18 <Epsilon>
<basic_statement> ==>
    19 <return_statement> |
    20 <if_statement> |
    21 <while_statement> |
    22 <declaration_statement> |
    23 <assignment_or_function_call>

    # 19 TokenType.KeywordReturn TokenType.Semicolon |
    # 20 TokenType.KeywordIf <remaining_if_statement> |
    # 21 TokenType.KeywordWhile <remaining_while_statement> |
    # 22 TokenType.KeywordVar TokenType.Identifier <datatype> TokenType.Semicolon |
    # 23 TokenType.Identifier <assignment_or_function_call> TokenType.Semicolon

<expression_list> ==>
    27 <expression> {, <expression>}

<code_block> ==>
    29 TokenType.OpenCurly <statement_list> TokenType.CloseCurly

<return_statement> ==>
    30 TokenType.KeywordReturn TokenType.Semicolon

<if_statement> ==>
    31 TokenType.KeywordIf TokenType.OpenParen <boolean_expression>
        TokenType.CloseParen <code_block> [ TokenType.KeywordElse <code_block> ]

<declaration_statement> ==>
    33 TokenType.KeywordVar TokenType.Identifier <datatype> TokenType.Semicolon

<while_statement> ==>
    34 TokenType.KeywordWhile TokenType.OpenParen <boolean_expression>
        TokenType.CloseParen <code_block>

<assignment_or_function_call> ==>
    24 TokenType.Identifier TokenType.AssignmentOperator <expression>
        TokenType.Semicolon |
    25 TokenType.Identifier TokenType.OpenBracket <expression>
        TokenType.CloseBracket TokenType.AssignmentOperator <expression>
        TokenType.Semicolon |
    26 TokenType.Identifier TokenType.OpenParen <expression_list>
        TokenType.CloseParen TokenType.Semicolon

<expression> ==>
    35 <term> { TokenType.AddSubOperator <term> }
<term> ==>
    39 <factor> { TokenType.MulDivModOperator <factor> }

<factor> ==>
    44 TokenType.OpenParen <expression> TokenType.CloseParen |
    45 TokenType.Identifier <variable_or_function_call> |
    46 <literal>

<variable_or_function_call> ==>
    49 TokenType.OpenBracket <expression> TokenType.CloseBracket |
    50 TokenType.OpenParen <expression_list> TokenType.CloseParen |
    51 <Epsilon>
<boolean_expression> ==>
    52 <expression> <boolean_comparator> <expression>
<boolean_comparator> ==>
    53 TokenType.EqualityOperator |
    54 TokenType.NotEqualOperator |
    55 TokenType.LessThanOperator |
    56 TokenType.LessThanOrEqualOp

<literal> ==>
    57 TokenType.Float |
    58 TokenType.Integer |
    59 TokenType.Char |
    60 TokenType.String

"""

from Token import TokenType, Token, DataTypes
from Scanner import Scanner
from FileReader import FileReader
from SymbolTable import SymbolTable #, IdType
from Errors import *
from CodeGenerator import CG
import os
import traceback


class Parser:
    """
    A class used to parse an input file into a parse tree.
    This is a singleton implementation of a Parser; I have chosen the
    singleton pattern because I don't think it makes any sense to have more
    than one Parser, and I need to keep some internal state associated
    with the Parser that I would prefer not to be global.
    """

    #################################################################
    # STATIC DATA MEMBERS
    # Data that models the current state of the Parser

    # file_reader: A File_Reader object that abstracts the work of dealing
    # with the input file. If this object were not made global to the parser,
    # then this variable would need to be passed into every recursive descent
    # function in the class.
    file_reader = None

    # s_table: A SymbolTable object that keeps track of symbols used in the
    # program
    s_table = None



    #################################################################
    # HELPER FUNCTIONS

    @staticmethod
    def parse(filename, asm_output_filename):
        """
        Uses recursive descent to parse an input file, printing a list of
        productions as it goes. Opens the input file, and calls 'program()',
        which begins recursive descent until an EndOfFile token is reached.
        If no errors occur, it prints "Success!!!"
        :param filename:    The name of the file to parse.
        :return:            None
        """
        with FileReader(filename) as fr:

            with open(asm_output_filename, 'w') as file_out:

                CG.init(file_out)

                Parser.file_reader = fr
                Parser.s_table = SymbolTable()
                current_token = Scanner.get_token(Parser.file_reader)
                Parser.program(current_token)
                Parser.match(current_token, TokenType.EndOfFile)

        if CG.is_code_ok:
            print("\nSuccess!!!")
        else:
            print("Compilation completed unsuccessfully.")
            os.remove(asm_output_filename)
        
    
    
    @staticmethod
    def match(current_token, expected_tt):
        """
        Matches the current token with an expected_tt token or token type,
        then reads the next token from the scanner.
        If a match cannot be made, raises a Parser.Error object.
        :param current_token:   The current token being read
        :param expected_tt:     The expected TokenType
        :return:                None
        """
        assert(isinstance(current_token, Token))
        assert(isinstance(expected_tt, TokenType))

        # If the current token matches the expected_tt token, or token type,
        if current_token.t_type == expected_tt:
            # then get the next token and put it in current_token
            current_token.assignTo(Scanner.get_token(Parser.file_reader))
        else:
            # otherwise, we have an error.
            line_data = Parser.file_reader.get_line_data()
            raise MatchError(
                "At line %d, column %d: " % (line_data["Line_Num"],
                                             line_data["Column"]) +
                "Tried to match %r with %r, but they were unequal.\n" %
                (current_token, expected_tt) +
                "%s" % line_data["Line"] +
                " " * line_data["Column"] + "^\n"
            )



    @staticmethod
    def skip_tokens_if_not(token_type, current_token):
        """
        Causes the scanner to skip past tokens until token_type is
        encountered. When the function returns, current_token will be a token
        with the type token_type.
        :param token_type:  The token type on which to stop.
        :return:            None
        """
        while current_token.t_type != token_type and \
                current_token.t_type != TokenType.EndOfFile:
            current_token.assignTo(Scanner.get_token(Parser.file_reader))


    
    @staticmethod
    def raise_production_not_found_error(current_token, non_terminal):
        """
        Gets data from the file reader and formats it as an error message
        """
        line_data = Parser.file_reader.get_line_data()
        raise ProductionNotFoundError(
            "At line %d, column %d: " % (line_data["Line_Num"],
                                         line_data["Column"]) +
            "Could not find a production for terminal %r in non-terminal %s" %
            (current_token, non_terminal) +
            "\n%s" % line_data["Line"] +
            " " * line_data["Column"] + "^\n"
        )



    @staticmethod
    def error_on_variable_usage(identifier, is_decl_stmt=False):
        """
        Verifies that an identifier has been is_decl_stmt before use, and is
        currently in an open scope. If not, raises an error.
        :param identifier:      An identifier being used.
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
                Parser.s_table.find_in_all_scopes(identifier) is None:
            # report an error
            line_data = Parser.file_reader.get_line_data()
            raise UseUndeclaredVariableError(
                "At line %d, column %d: " % (line_data["Line_Num"],
                                             line_data["Column"]) +
                "Attempt to use undeclared variable %s.\n" % identifier +
                "%s" % line_data["Line"] +
                " " * line_data["Column"] + "^\n"
            )
        # if we are declaring the variable that has already been
        # declared in this scope,
        elif is_decl_stmt and Parser.s_table.find(identifier) is not None:
            # report an error
            line_data = Parser.file_reader.get_line_data()
            raise RedeclaredVariableError(
                "At line %d, column %d: " % (line_data["Line_Num"],
                                             line_data["Column"]) +
                "Attempt to redeclare variable %s.\n" % identifier +
                "%s" % line_data["Line"] +
                " " * line_data["Column"] + "^\n"
            )



    @staticmethod
    def display_symbol_table():
        """
        Prints the symbol table to the screen
        """
        if Parser.s_table:
            Parser.s_table.display()
        else:
            print("Parser symbol table uninitialized")

    
    
    #################################################################
    # RECURSIVE DESCENT FUNCTIONS

    @staticmethod
    def program(token):
        """
        Implements recursive descent for the rule:
        <program> ==>
            <function_decl> {<function_decl>} |
            <Epsilon>
        """
        CG.write_prolog()
        if token.t_type in (TokenType.KeywordFunc,):
            while token.t_type in (TokenType.KeywordFunc,):
                print(1, end=" ")
                Parser.function_decl(token)
        else:
            print(2, end=" ")

        CG.write_epilogue()



    @staticmethod
    def function_decl(token):
        """
        Implements recursive descent for the rule:
        <function_decl> ==>
            TokenType.KeywordFunc TokenType.Identifier
            TokenType.OpenParen <param_list> TokenType.CloseParen
            <return_identifier> <return_datatype>
            TokenType.OpenCurly <statement_list> TokenType.CloseCurly
        """
        if token.t_type == TokenType.KeywordFunc:
            print("")
            print(3, end=" ")
            Parser.match(token, TokenType.KeywordFunc)

            # add the function identifier to the symbol table
            function_id = token.lexeme

            # check that the identifier hasn't already been declared
            Parser.error_on_variable_usage(function_id, is_decl_stmt=True)

            function_dict = {}
            Parser.s_table.insert(function_id, function_dict)

            # open a new scope
            Parser.s_table.open_scope()

            Parser.match(token, TokenType.Identifier)
            Parser.match(token, TokenType.OpenParen)
            Parser.param_list(token)
            Parser.match(token, TokenType.CloseParen)

            return_val_id = token.lexeme
            Parser.return_identifier(token)
            return_val_type = Parser.return_datatype(token)

            er_return_val = CG.declare_variable(return_val_type, return_val_id)
            Parser.s_table.insert(return_val_id, er_return_val)

            function_dict["return_type"] = return_val_type
            function_dict["type"] = \
                DataTypes.function_that_returns_type(return_val_type)
            function_dict["return_val_id"] = return_val_id
            function_dict["label"] = CG.gen_function_label(function_id)
            # TODO: fit param list into function_dict

            CG.code_gen_label(function_dict["label"],
                              "Returns %r in variable %s" %
                              (return_val_type, return_val_id))

            Parser.match(token, TokenType.OpenCurly)
            Parser.statement_list(token)
            Parser.match(token, TokenType.CloseCurly)

            # close the function's scope
            Parser.s_table.close_scope()

            # reset the stack offsets
            CG.next_offset = 0
        else:
            Parser.raise_production_not_found_error(token, 'function_decl')



    @staticmethod
    def param_list(token):
        """
        Implements recursive descent for the rule:
            <param_list> ==>
                4 TokenType.Identifier <datatype>
                    {TokenType.Comma TokenType.Identifier <datatype>} |
                5 <Epsilon>
        Also inserts an identifier into the symbol table
        :return:    a list of ExpressionRecords that reference the param list
        """
        params = []
        if token.t_type == TokenType.Identifier:
            print(4, end=" ")

            # We will handle each entry in the list the same way, except if
            # it's not the first entry, we will consume comma tokens before
            # each entry.

            first_parameter = True      # tells us if this is the first param

            while first_parameter or token.t_type is TokenType.Comma:

                if first_parameter:
                    # Next time, remember that we need to read commas here.
                    first_parameter = False
                else:
                    # Consume a comma
                    Parser.match(token, TokenType.Comma)

                # get the param's identifier and datatype
                identifier = token.lexeme
                Parser.match(token, TokenType.Identifier)
                datatype = Parser.datatype(token)

                # check that the identifier hasn't already been declared
                Parser.error_on_variable_usage(identifier, is_decl_stmt=True)

                # reserve space on the stack for the variable
                var_er = CG.declare_variable(datatype, identifier)

                # add the parameter to the param_list
                params.append(var_er)

                # insert the identifier into the symbol table
                Parser.s_table.insert(identifier, var_er)

        else:
            print(5, end=" ")
        return params



    @staticmethod
    def datatype(token):
        """
        Implements recursive descent for the rule:
        <datatype> ==>
            TokenType.KeywordInt |
            TokenType.KeywordFloat |
            TokenType.KeywordChar |
            TokenType.OpenBracket TokenType.Integer TokenType.CloseBracket
            <array_of_datatype>
        :return:    The datatype, as a Token.Datatypes enum
        """
        if token.t_type == TokenType.KeywordInt:
            print(8, end=" ")
            Parser.match(token, TokenType.KeywordInt)
            return DataTypes.INT
        elif token.t_type == TokenType.KeywordFloat:
            print(9, end=" ")
            Parser.match(token, TokenType.KeywordFloat)
            return DataTypes.FLOAT
        elif token.t_type == TokenType.KeywordChar:
            print(10, end=" ")
            Parser.match(token, TokenType.KeywordChar)
            return DataTypes.CHAR
        elif token.t_type == TokenType.OpenBracket:
            print(11, end=" ")
            Parser.match(token, TokenType.OpenBracket)
            Parser.match(token, TokenType.Integer)
            Parser.match(token, TokenType.CloseBracket)
            return Parser.array_of_datatype(token)
        else:
            Parser.raise_production_not_found_error(token, 'datatype')



    @staticmethod
    def array_of_datatype(token):
        """
        Implements recursive descent for the rule:
        <array_of_datatype> ==>
            TokenType.KeywordInt |
            TokenType.KeywordFloat |
            TokenType.KeywordChar
        :return:    The datatype, as a SymbolTable.IdType enum
        """
        if token.t_type == TokenType.KeywordInt:
            print(12, end=" ")
            Parser.match(token, TokenType.KeywordInt)
            return DataTypes.ARRAY_INT
        elif token.t_type == TokenType.KeywordFloat:
            print(13, end=" ")
            Parser.match(token, TokenType.KeywordFloat)
            return  DataTypes.ARRAY_FLOAT
        elif token.t_type == TokenType.KeywordChar:
            print(14, end=" ")
            Parser.match(token, TokenType.KeywordChar)
            return DataTypes.ARRAY_CHAR
        else:
            Parser.raise_production_not_found_error(token, 'array_of_datatype')



    @staticmethod
    def return_identifier(token):
        """
        Implements recursive descent for the rule:
        <return_identifier> ==>
            TokenType.Identifier
        """
        if token.t_type == TokenType.Identifier:
            print(15, end=" ")
            Parser.match(token, TokenType.Identifier)
        else:
            Parser.raise_production_not_found_error(token, 'return_identifier')



    @staticmethod
    def return_datatype(token):
        """
        Implements recursive descent for the rule:
        <return_datatype> ==>
            <datatype>
        :return:    The datatype, as a SymbolTable.IdType enum
        """
        if token.t_type in (TokenType.KeywordInt, TokenType.KeywordFloat,
                      TokenType.KeywordChar, TokenType.OpenBracket):
            print(16, end=" ")
            return Parser.datatype(token)
        else:
            Parser.raise_production_not_found_error(token, 'return_datatype')



    @staticmethod
    def statement_list(token):
        """
        Implements recursive descent for the rule:
        <statement_list> ==>
            <basic_statement> {<basic_statement>} |
            <Epsilon>
        """
        if token.t_type in (TokenType.KeywordReturn, TokenType.KeywordIf,
                            TokenType.KeywordWhile, TokenType.KeywordVar,
                            TokenType.Identifier):
            while token.t_type in (TokenType.KeywordReturn, TokenType.KeywordIf,
                            TokenType.KeywordWhile, TokenType.KeywordVar,
                            TokenType.Identifier):
                print("")
                print(17, end=" ")
                Parser.basic_statement(token)
        else:
            print(18, end=" ")



    @staticmethod
    def basic_statement(token):
        """
        Implements recursive descent for the rule:
        <basic_statement> ==>
            19 <return_statement> |
            20 <if_statement> |
            21 <while_statement> |
            22 <declaration_statement> |
            23 <assignment_or_function_call>
        """
        if token.t_type == TokenType.KeywordReturn:
            print(19, end=" ")
            Parser.return_statement(token)
        elif token.t_type == TokenType.KeywordIf:
            print(20, end=" ")
            Parser.if_statement(token)
        elif token.t_type == TokenType.KeywordWhile:
            print(21, end=" ")
            Parser.while_statement(token)
        elif token.t_type == TokenType.KeywordVar:
            print(22, end=" ")
            Parser.declaration_statement(token)
        elif token.t_type == TokenType.Identifier:
            print(23, end=" ")
            Parser.assignment_or_function_call(token)
        else:
            Parser.raise_production_not_found_error(token, 'basic_statement')



    @staticmethod
    def expression_list(token):
        """
        Implements recursive descent for the rule:
        <expression_list> ==>
            <expression> {, <expression>} |
            <Epsilon>
        """
        if token.t_type in \
                (TokenType.OpenParen, TokenType.Identifier, TokenType.Float,
                 TokenType.Integer, TokenType.String):
            print(27, end=" ")
            Parser.expression(token)
            while token.t_type == TokenType.Comma:
                Parser.match(token, TokenType.Comma)
                Parser.expression(token)
        else:
            print(28, end=" ")



    @staticmethod
    def code_block(token):
        """
        Implements recursive descent for the rule:
        <code_block> ==>
            29 TokenType.OpenCurly <statement_list> TokenType.CloseCurly
        Also attempts to recover from errors: within a block, upon
        encountering a Parser.Error exception, it skips past any tokens until
        it reaches a CloseCurly, and then resumes normally.
        """
        if token.t_type == TokenType.OpenCurly:
            print(29, end=" ")
            Parser.match(token, TokenType.OpenCurly)

            Parser.s_table.open_scope()
            # Parse statement list, with error recovery on }
            try:
                Parser.statement_list(token)
            except ParseError as ex:
                # print("\nException occurred while parsing code block:\n%s" % ex)
                print(traceback.format_exc())
                Parser.skip_tokens_if_not(TokenType.CloseCurly, token)

            Parser.match(token, TokenType.CloseCurly)
            Parser.s_table.close_scope()
        else:
            Parser.raise_production_not_found_error(token, 'code_block')



    @staticmethod
    def return_statement(token):
        """
        Implements recursive descent for the rule:
        <return_statement> ==>
            30 TokenType.KeywordReturn TokenType.Semicolon
        """
        if token.t_type == TokenType.KeywordReturn:
            print(30, end="")
            Parser.match(token, TokenType.KeywordReturn)
            Parser.match(token, TokenType.Semicolon)



    @staticmethod
    def if_statement(token):
        """
        Implements recursive descent for the rule:
        <if_statement> ==>
            31 TokenType.KeywordIf TokenType.OpenParen <boolean_expression>
                TokenType.CloseParen <code_block> [ <else_clause> ]
        """
        if token.t_type == TokenType.KeywordIf:
            print(31, end=" ")
            Parser.match(token, TokenType.KeywordIf)
            Parser.match(token, TokenType.OpenParen)
            Parser.boolean_expression(token)
            Parser.match(token, TokenType.CloseParen)

            Parser.code_block(token)

            if token.t_type == TokenType.KeywordElse:
                Parser.match(token, TokenType.KeywordElse)
                Parser.code_block(token)
        else:
            Parser.raise_production_not_found_error(
                token, 'if_statement')



    @staticmethod
    def declaration_statement(token):
        """
        Implements recursive descent for the rule:
        <declaration_statement> ==>
            TokenType.KeywordVar TokenType.Identifier <datatype>
            TokenType.Semicolon
        """
        if token.t_type == TokenType.KeywordVar:
            print(33, end=" ")
            Parser.match(token, TokenType.KeywordVar)

            # get the param's identifier and datatype
            identifier = token.lexeme
            Parser.match(token, TokenType.Identifier)
            datatype = Parser.datatype(token)

            # check that the identifier hasn't already been declared
            Parser.error_on_variable_usage(identifier, True)

            # reserve space on the stack for the variable
            var_er = CG.declare_variable(datatype, identifier)

            # insert the identifier into the symbol table
            Parser.s_table.insert(identifier, var_er)

            Parser.match(token, TokenType.Semicolon)
        else:
            Parser.raise_production_not_found_error(
                token, 'declaration_statement')



    @staticmethod
    def while_statement(token):
        """
        Implements recursive descent for the rule:
        <while_statement> ==>
            34 TokenType.KeywordWhile TokenType.OpenParen <boolean_expression>
                TokenType.CloseParen <code_block>
        """
        if token.t_type == TokenType.KeywordWhile:
            print(34, end=" ")
            Parser.match(token, TokenType.KeywordWhile)
            Parser.match(token, TokenType.OpenParen)
            Parser.boolean_expression(token)
            Parser.match(token, TokenType.CloseParen)
            Parser.code_block(token)
        else:
            Parser.raise_production_not_found_error(
                token, 'while_statement')



    @staticmethod
    def assignment_or_function_call(token):
        """
        Implements recursive descent for the rule:
        <assignment_or_function_call> ==>
            24 TokenType.Identifier TokenType.AssignmentOperator <expression>
                TokenType.Semicolon |
            25 TokenType.Identifier TokenType.OpenBracket <expression>
                TokenType.CloseBracket TokenType.AssignmentOperator <expression>
                TokenType.Semicolon |
            26 TokenType.Identifier TokenType.OpenParen <expression_list>
                TokenType.CloseParen TokenType.Semicolon
        """
        if token.t_type == TokenType.Identifier:
            # get the param's identifier and look it up
            identifier = token.lexeme
            Parser.error_on_variable_usage(identifier)
            er_lhs = Parser.s_table.find_in_all_scopes(identifier)

            Parser.match(token, TokenType.Identifier)

            if token.t_type == TokenType.AssignmentOperator:
                print(24, end=" ")
                CG.code_gen_comment(Parser.file_reader.current_line.strip())
                Parser.match(token, TokenType.AssignmentOperator)
                er_rhs = Parser.expression(token)
                Parser.match(token, TokenType.Semicolon)
                CG.code_gen_assign(er_lhs, er_rhs)
            elif token.t_type == TokenType.OpenBracket:
                print(25, end=" ")
                Parser.match(token, TokenType.OpenBracket)
                er_subscript = Parser.expression(token)
                Parser.match(token, TokenType.CloseBracket)

                er_lhs = CG.array_subscript_to_stack_entry(er_lhs, er_subscript)

                Parser.match(token, TokenType.AssignmentOperator)
                er_rhs = Parser.expression(token)
                Parser.match(token, TokenType.Semicolon)
                CG.code_gen_assign(er_lhs, er_rhs)
            elif token.t_type == TokenType.OpenParen:
                print(26, end=" ")
                Parser.match(token, TokenType.OpenParen)
                Parser.expression_list(token)
                Parser.match(token, TokenType.CloseParen)
                Parser.match(token, TokenType.Semicolon)

                # TODO: implement function calls
                # er_rhs = call function with params
                #CG.code_gen_assign(er_lhs, er_rhs)
            else:
                Parser.raise_production_not_found_error(
                    token, 'assignment_or_function_call')
        else:
            Parser.raise_production_not_found_error(
                token, 'assignment_or_function_call')

    @staticmethod
    def expression(token):
        """
        Implements recursive descent for the rule:
        <expression> ==>
            35 <term> { TokenType.AddSubOperator <term> }
        """
        if token.t_type in (TokenType.OpenParen, TokenType.Identifier,
                            TokenType.Float, TokenType.Integer, TokenType.String):
            print(35, end=" ")

            erL = Parser.term(token)
            while token.t_type == TokenType.AddSubOperator:
                operator = token.lexeme
                Parser.match(token, TokenType.AddSubOperator)
                erR = Parser.term(token)
                erL = CG.gen_expression(erL, erR, operator)
            return erL
        else:
            Parser.raise_production_not_found_error(token, 'expression')



    @staticmethod
    def term(token):
        """
        Implements recursive descent for the rule:
        <term> ==>
            39 <factor> { TokenType.MulDivModOperator <factor> }
        """
        if token.t_type in (TokenType.OpenParen, TokenType.Identifier,
                            TokenType.Float, TokenType.Integer, TokenType.String):
            print(39, end=" ")
            erL = Parser.factor(token)
            while token.t_type == TokenType.MulDivModOperator:
                operator = token.lexeme
                Parser.match(token, TokenType.MulDivModOperator)
                erR = Parser.factor(token)
                erL = CG.gen_expression(erL, erR, operator)
            return erL
        else:
            Parser.raise_production_not_found_error(token, 'term')



    @staticmethod
    def factor(token):
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
            Parser.match(token, TokenType.OpenParen)
            exp_rec = Parser.expression(token)
            Parser.match(token, TokenType.CloseParen)
            return exp_rec
        elif token.t_type == TokenType.Identifier:
            print(45, end=" ")

            # Check to be sure that it has been declared in an open scope
            Parser.error_on_variable_usage(token.lexeme)

            exp_rec = Parser.s_table.find_in_all_scopes(token.lexeme)

            Parser.match(token, TokenType.Identifier)

            # TODO: connect function return value/array subscript to exp_rec
            Parser.variable_or_function_call(token)
            return exp_rec

        elif token.t_type in (TokenType.Float, TokenType.Integer,
                              TokenType.Char, TokenType.String):
            return Parser.literal(token)
        else:
            Parser.raise_production_not_found_error(token, 'factor')



    @staticmethod
    def literal(token):
        """
        Implements recursive descent for the rule:
        <literal> ==>
             57 TokenType.Float |
             58 TokenType.Integer |
             59 TokenType.Char |
             60 TokenType.String
        """
        er_literal = None
        if token.t_type == TokenType.Float:
            print(57, end=" ")
            er_literal = CG.create_literal(DataTypes.FLOAT, float(token.lexeme))
            Parser.match(token, TokenType.Float)
        elif token.t_type == TokenType.Integer:
            print(58, end=" ")
            er_literal = CG.create_literal(DataTypes.INT, int(token.lexeme))
            Parser.match(token, TokenType.Integer)
        elif token.t_type == TokenType.String:
            print(59, end=" ")
            er_literal = CG.create_literal(DataTypes.STRING, token.lexeme)
            Parser.match(token, TokenType.String)
        elif token.t_type == TokenType.Char:
            print(60, end=" ")
            er_literal = CG.create_literal(DataTypes.CHAR, token.lexeme)
            Parser.match(token, TokenType.String)
        return er_literal



    @staticmethod
    def variable_or_function_call(token):
        """
        Implements recursive descent for the rule:
        <variable_or_function_call> ==>
            TokenType.OpenBracket <expression> TokenType.CloseBracket |
            TokenType.OpenParen <expression_list> TokenType.CloseParen |
            <Epsilon>
        """
        if token.t_type == TokenType.OpenBracket:
            print(49, end=" ")
            Parser.match(token, TokenType.OpenBracket)
            Parser.expression(token)
            Parser.match(token, TokenType.CloseBracket)
        elif token.t_type == TokenType.OpenParen:
            print(50, end=" ")
            Parser.match(token, TokenType.OpenParen)
            Parser.expression_list(token)
            Parser.match(token, TokenType.CloseParen)
        else:
            print(51, end=" ")



    @staticmethod
    def boolean_expression(token):
        """
        Implements recursive descent for the rule:
        <boolean_expression> ==>
            <expression> <boolean_comparator> <expression>
        """
        if token.t_type in (TokenType.OpenParen, TokenType.Identifier,
                            TokenType.Float, TokenType.Integer, TokenType.String):
            print(52, end=" ")
            Parser.expression(token)
            Parser.boolean_comparator(token)
            Parser.expression(token)
        else:
            Parser.raise_production_not_found_error(
                token, 'boolean_expression')



    @staticmethod
    def boolean_comparator(token):
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
            Parser.match(token, TokenType.EqualityOperator)
        elif token.t_type == TokenType.NotEqualOperator:
            print(54, end=" ")
            Parser.match(token, TokenType.NotEqualOperator)
        elif token.t_type == TokenType.LessThanOperator:
            print(55, end=" ")
            Parser.match(token, TokenType.LessThanOperator)
        elif token.t_type == TokenType.LessThanOrEqualOp:
            print(56, end=" ")
            Parser.match(token, TokenType.LessThanOrEqualOp)
        else:
            Parser.raise_production_not_found_error(
                token, 'boolean_comparator')



test_file_dir = "/home/dave/PycharmProjects/Compiler/testParserST/"
# "C:/Users/Dave/PycharmProjects/compiler/unusedTestPrograms/" #
output_file_dir = "/home/dave/PycharmProjects/Compiler/asmOutput/"
# "C:/Users/Dave/PycharmProjects/compiler/asmOutput/" #


if __name__ == "__main__":
    # For every file in the test file directory,
    for f in os.listdir(test_file_dir):

        # Prepend the path of the test file directory
        input_filename = test_file_dir + f

        output_filename = output_file_dir + f

        print("\nParsing file " + f)

        try:
            Parser.parse(input_filename, output_filename)
        except Exception as ex:
            print('\n' + traceback.format_exc())
            # print("\nException occurred while parsing file %s:\n%s" % (f, ex))

        Parser.display_symbol_table()
