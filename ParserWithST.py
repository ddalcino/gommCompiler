"""
Filename: ParserWithST.py
Tested using Python 3.5.1

David Dalcino
CS 6110
Prof. Reiter
Winter 2017
CSU East Bay

Parser With Code Generation


This file implements a parser, using recursive descent. All of the
recursive descent functions are generated from the grammar by another script;
the product of this script has been edited by hand to add symbol table
functionality.

The grammar implemented is summarized here:
<program> ==>
    1 {<func_decl_or_proto>} |
<func_decl_or_proto> ==>
    2 <function_decl> |
    3 <function_prototype>

<function_prototype> ==>
    4 TokenType.KeywordProto TokenType.Identifier TokenType.OpenParen
        <param_list> TokenType.CloseParen <return_identifier> <return_datatype>
        TokenType.Semicolon
<function_decl> ==>
    5 TokenType.KeywordFunc TokenType.Identifier TokenType.OpenParen
        <param_list> TokenType.CloseParen <return_identifier> <return_datatype>
        TokenType.OpenCurly <statement_list> TokenType.CloseCurly
<param_list> ==>
    6  [ TokenType.Identifier <datatype>
        {TokenType.Comma TokenType.Identifier <datatype>} ]
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

<expression_list> ==>
    27 <expression> {, <expression>}

<code_block> ==>
    29 TokenType.OpenCurly <statement_list> TokenType.CloseCurly

<return_statement> ==>
    30 TokenType.KeywordReturn TokenType.Semicolon

<if_statement> ==>
    31 TokenType.KeywordIf TokenType.OpenParen <expression>
        TokenType.CloseParen <code_block> [ TokenType.KeywordElse <code_block> ]

<declaration_statement> ==>
    33 TokenType.KeywordVar TokenType.Identifier <datatype> TokenType.Semicolon

<while_statement> ==>
    34 TokenType.KeywordWhile TokenType.OpenParen <expression>
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
    39 <relfactor> { TokenType.MulDivModOperator <relfactor> }
<relfactor> ==>
    40 <factor> [TokenType.RelationalOperator <factor>]

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

from Token import TokenType, Token
from Scanner import Scanner
from FileReader import FileReader
from SymbolTable import SymbolTable
from Errors import *
from CodeGenerator import CG
from ExpressionRecord import ExpressionRecord, FunctionSignature, DataTypes
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
        :return:            True if compiled successfully; else False
        """
        with FileReader(filename) as fr:

            with open(asm_output_filename, 'w') as file_out:

                CG.init(file_out, fr)

                Parser.file_reader = fr
                Parser.s_table = SymbolTable()
                current_token = Scanner.get_token(Parser.file_reader)
                Parser.program(current_token)
                Parser.match(current_token, TokenType.EndOfFile)

                # Search for main in open symbol table:
                # if not found, compilation has failed
                if not Parser.s_table.find("main"):
                    print("No main function found in program; point of entry "
                          "required")
                    CG.is_code_ok = False

                # Search for FunctionSignatures in the symbol table,
                # and check that each has been defined; if not, compilation
                # has failed
                undefined_proto_ids = Parser.s_table.get_undefined_prototypes()
                for func_id in undefined_proto_ids:
                    print("Function %s was forward declared, but was never "
                          "defined." % func_id)
                    CG.is_code_ok = False


        if CG.is_code_ok:
            print("\nSuccess!!!")
            return True
        else:
            print("Compilation completed unsuccessfully.")
            os.remove(asm_output_filename)
            return False
        
    
    
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
                "Expected %r but found %r, but they were unequal.\n" %
                (expected_tt, current_token) +
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
    def error_on_variable_usage(identifier, is_decl_stmt=False,
                                is_prototype=False):
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
        :param is_prototype:    TODO
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

        # previously defined record of identifier
        prev_record = Parser.s_table.find(identifier)

        # if we are declaring the variable that has already been
        # declared in this scope,
        if is_decl_stmt and prev_record is not None:

            # if prev_record is a prototype FunctionSignature, and the new
            # declaration is not a prototype, then it's the first definition
            # of the function.
            # Any other case is an error.
            if isinstance(prev_record, FunctionSignature) and \
                    prev_record.is_prototype and not is_prototype:
                return

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
        """ Prints the symbol table to the screen """
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
            1 {<func_decl_or_proto>} |
        """
        CG.write_prolog()
        CG.write_epilogue()

        print(1, end=" ")
        if token.t_type in (TokenType.KeywordFunc, TokenType.KeywordProto):
            while token.t_type in (TokenType.KeywordFunc,
                                   TokenType.KeywordProto):
                Parser.func_decl_or_proto(token)



    @staticmethod
    def func_decl_or_proto(token):
        """
        Implements recursive descent for the rule:
        <func_decl_or_proto> ==>
            2 <function_decl> |
            3 <function_prototype>
        """
        print("")           # Newline, for readability
        if token.t_type == TokenType.KeywordFunc:
            print(2, end=" ")
            Parser.function_decl(token)
        elif token.t_type == TokenType.KeywordProto:
            print(3, end=" ")
            Parser.function_prototype(token)
        else:
            Parser.raise_production_not_found_error(token, 'func_decl_or_proto')



    @staticmethod
    def function_prototype(token):
        """
        Implements recursive descent for the rule:
        <function_prototype> ==>
            4   TokenType.KeywordProto TokenType.Identifier TokenType.OpenParen
                <param_list> TokenType.CloseParen <return_identifier>
                <return_datatype> TokenType.Semicolon
        """
        if token.t_type == TokenType.KeywordProto:
            print(4, end=" ")
            Parser.match(token, TokenType.KeywordProto)

            # add the function identifier to the symbol table
            function_id = token.lexeme

            # check that the identifier hasn't already been declared
            Parser.error_on_variable_usage(function_id, is_decl_stmt=True,
                                           is_prototype=True)

            Parser.match(token, TokenType.Identifier)
            Parser.match(token, TokenType.OpenParen)

            param_list = Parser.param_list(token)
            param_types = [x[1] for x in param_list]

            Parser.match(token, TokenType.CloseParen)

            Parser.return_identifier(token)
            return_val_type = Parser.return_datatype(token)

            func_signature = FunctionSignature(
                identifier=function_id,
                label=CG.gen_function_label(function_id),
                param_list_types=param_types,
                return_type=return_val_type,
                is_prototype=True)
            Parser.s_table.insert(function_id, func_signature)
            Parser.match(token, TokenType.Semicolon)



    @staticmethod
    def function_decl(token):
        """
        Implements recursive descent for the rule:
        <function_decl> ==>
            5   TokenType.KeywordFunc TokenType.Identifier
                TokenType.OpenParen <param_list> TokenType.CloseParen
                <return_identifier> <return_datatype>
                TokenType.OpenCurly <statement_list> TokenType.CloseCurly
        """
        if token.t_type == TokenType.KeywordFunc:
            print(5, end=" ")
            Parser.match(token, TokenType.KeywordFunc)

            # add the function identifier to the symbol table
            function_id = token.lexeme

            # check that the identifier hasn't already been declared
            Parser.error_on_variable_usage(function_id, is_decl_stmt=True)

            func_signature = FunctionSignature(function_id)

            old_signature = Parser.s_table.find_in_all_scopes(function_id)
            if not old_signature:
                # we don't need to check that signatures match
                Parser.s_table.insert(function_id, func_signature)
            elif not isinstance(old_signature, FunctionSignature):
                raise SemanticError("Tried to redeclare %s as a function, "
                                    "but it was already a variable" %
                                    function_id,
                                    Parser.file_reader.get_line_data())

            # open a new scope
            Parser.s_table.open_scope()

            Parser.match(token, TokenType.Identifier)
            Parser.match(token, TokenType.OpenParen)

            param_list = Parser.param_list(token)
            param_types = [x[1] for x in param_list]

            if not old_signature:
                func_signature.param_list_types = param_types
            else:
                # verify that param types match
                for i in range(len(param_types)):
                    if param_types[i] != old_signature.param_list_types[i]:
                        raise SemanticError(
                            "In declaration of function %s, parameter #%d is "
                            "of type %r, but previous forward declaration was "
                            "of type %r" % (function_id, i, param_types[i],
                                            old_signature.param_list_types[i]),
                            Parser.file_reader.get_line_data())

            Parser.match(token, TokenType.CloseParen)

            return_val_id = token.lexeme
            Parser.return_identifier(token)
            return_val_type = Parser.return_datatype(token)

            er_return_val = ExpressionRecord(
                return_val_type, (4*len(param_list)+4), is_temp=False)
            Parser.s_table.insert(return_val_id, er_return_val)

            if not old_signature:
                func_signature.return_type = return_val_type
                func_signature.label = CG.gen_function_label(function_id)
            else:
                # verify that return types match
                if return_val_type != old_signature.return_type:
                    raise SemanticError(
                        "In declaration of function %s, return datatype is "
                        "of type %r, but previous forward declaration was "
                        "of type %r" % (function_id, return_val_type,
                                        old_signature.return_type),
                        Parser.file_reader.get_line_data())

                # at this point, we are guaranteed that the return types,
                # param types, and identifier are equal to that of the old
                # signature, so we can use that signature instead
                func_signature = old_signature

                # record that the signature has been defined
                old_signature.is_prototype = False

            CG.code_gen_label(func_signature.label, comment=str(func_signature))

            offset = (4*len(param_list))

            # In new function, return var is at (4*len(params)+8)($fp),
            # params are at 4($fp) thru (4*len(params)+4)($fp)
            for identifier, data_type, size in param_list:

                er_param = ExpressionRecord(data_type, offset,
                                            is_temp=False, is_reference=True)
                Parser.s_table.insert(identifier, er_param)

                offset -= 4

            Parser.match(token, TokenType.OpenCurly)
            Parser.statement_list(token)
            Parser.match(token, TokenType.CloseCurly)

            # close the function's scope
            Parser.s_table.close_scope()

            # reset the stack offsets
            CG.next_offset = -8

            CG.code_gen("jr", "$ra")
        else:
            Parser.raise_production_not_found_error(token, 'function_decl')



    @staticmethod
    def param_list(token):
        """
        Implements recursive descent for the rule:
            <param_list> ==>
                6  [ TokenType.Identifier <datatype>
                    {TokenType.Comma TokenType.Identifier <datatype>} ]
        :return:    a list of (name, type, size) tuples that define the params
        """
        params = []
        print(6, end=" ")

        if token.t_type == TokenType.Identifier:

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
                datatype, size = Parser.datatype(token)

                # add the parameter to the param_list
                params.append((identifier, datatype, size))

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
        :return:    A tuple in the form (Token.DataTypes, size), where size
                    is the number of words that must be allocated to a
                    variable of this datatype. Unless it's an array, size is
                    always 1.
        """
        if token.t_type == TokenType.KeywordInt:
            print(8, end=" ")
            Parser.match(token, TokenType.KeywordInt)
            return DataTypes.INT, 1
        elif token.t_type == TokenType.KeywordFloat:
            print(9, end=" ")
            Parser.match(token, TokenType.KeywordFloat)
            return DataTypes.FLOAT, 1
        elif token.t_type == TokenType.KeywordChar:
            print(10, end=" ")
            Parser.match(token, TokenType.KeywordChar)
            return DataTypes.CHAR, 1
        elif token.t_type == TokenType.OpenBracket:
            print(11, end=" ")
            Parser.match(token, TokenType.OpenBracket)
            size_str = token.lexeme
            Parser.match(token, TokenType.Integer)
            Parser.match(token, TokenType.CloseBracket)
            return Parser.array_of_datatype(token), int(size_str)
        else:
            Parser.raise_production_not_found_error(token, 'datatype')



    @staticmethod
    def array_of_datatype(token):
        """
        Implements recursive descent for the rule:
        <array_of_datatype> ==>
            12 TokenType.KeywordInt |
            13 TokenType.KeywordFloat |
            14 TokenType.KeywordChar
        :return:    The datatype, as a DataTypes enum
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
            data_type, size = Parser.datatype(token)
            if size == 1:
                return data_type
            else:
                raise SemanticError("Function cannot return an array",
                                    Parser.file_reader)
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
                print("")           # Newline, for readability of output
                print(17, end=" ")

                # Parse <basic_statement>, but recover if any errors occur,
                # and advance past the next semicolon
                try:
                    Parser.basic_statement(token)
                except ParseError:
                    CG.is_code_ok = False
                    print(traceback.format_exc())
                    Parser.skip_tokens_if_not(TokenType.Semicolon, token)
                    Parser.match(token, TokenType.Semicolon)

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
        # Print the statement as a comment
        CG.code_gen_comment(Parser.file_reader.current_line.strip())

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
        return_list = []
        if token.t_type in \
                (TokenType.OpenParen, TokenType.Identifier, TokenType.Float,
                 TokenType.Integer, TokenType.String, TokenType.Char):
            print(27, end=" ")
            return_list.append(Parser.expression(token))
            while token.t_type == TokenType.Comma:
                Parser.match(token, TokenType.Comma)
                return_list.append(Parser.expression(token))
        else:
            print(28, end=" ")
        return return_list



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

            next_offset_before_block = CG.next_offset

            Parser.statement_list(token)

            Parser.match(token, TokenType.CloseCurly)
            Parser.s_table.close_scope()

            # Reclaim stack space allocated within block, since it has gone
            # out of scope
            CG.next_offset = next_offset_before_block

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
            CG.code_gen("jr", "$ra")
        else:
            Parser.raise_production_not_found_error(token, 'return_statement')



    @staticmethod
    def if_statement(token):
        """
        Implements recursive descent for the rule:
        <if_statement> ==>
            31 TokenType.KeywordIf TokenType.OpenParen <expression>
                TokenType.CloseParen <code_block> [ <else_clause> ]
        """
        if token.t_type == TokenType.KeywordIf:
            print(31, end=" ")
            Parser.match(token, TokenType.KeywordIf)
            Parser.match(token, TokenType.OpenParen)
            er_condition = Parser.expression(token)
            if er_condition.data_type != DataTypes.BOOL:
                raise SemanticError("If statement requires boolean expression "
                                    "as an argument",
                                    Parser.file_reader.get_line_data())
            Parser.match(token, TokenType.CloseParen)

            else_label, after_else_label = CG.gen_label("else")
            CG.code_gen_if(er_condition, else_label)

            Parser.code_block(token)

            if token.t_type == TokenType.KeywordElse:
                Parser.match(token, TokenType.KeywordElse)

                # the last code block must branch to after the else clause
                CG.code_gen("b", after_else_label)

                # if test failed, then pick up program execution here
                CG.code_gen_label(else_label)

                # generate the else block
                Parser.code_block(token)

                # make the after_else label
                CG.code_gen_label(after_else_label)

            else:
                # if test failed, then pick up program execution here
                CG.code_gen_label(else_label)

        else:
            Parser.raise_production_not_found_error(
                token, 'if_statement')



    @staticmethod
    def declaration_statement(token):
        """
        Implements recursive descent for the rule:
        <declaration_statement> ==>
            33  TokenType.KeywordVar TokenType.Identifier <datatype>
                TokenType.Semicolon
        """
        if token.t_type == TokenType.KeywordVar:
            print(33, end=" ")
            Parser.match(token, TokenType.KeywordVar)

            # get the param's identifier and datatype
            identifier = token.lexeme
            Parser.match(token, TokenType.Identifier)
            datatype, size = Parser.datatype(token)

            # check that the identifier hasn't already been declared
            Parser.error_on_variable_usage(identifier, True)

            # reserve space on the stack for the variable
            var_er = CG.declare_variable(datatype, identifier, size)

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
            34  TokenType.KeywordWhile TokenType.OpenParen <expression>
                TokenType.CloseParen <code_block>
        """
        if token.t_type == TokenType.KeywordWhile:
            print(34, end=" ")
            before_while_lbl, after_while_lbl = CG.gen_label("while")

            # Write label for beginning of while loop
            CG.code_gen_label(before_while_lbl)

            Parser.match(token, TokenType.KeywordWhile)
            Parser.match(token, TokenType.OpenParen)
            er_condition = Parser.expression(token)
            Parser.match(token, TokenType.CloseParen)

            # Perform the test
            CG.code_gen_if(er_condition, after_while_lbl)

            # Write the contents of the loop
            Parser.code_block(token)

            # Branch back to the test again
            CG.code_gen("b", before_while_lbl)

            # Write label for end of while loop, to pick up when the test fails
            CG.code_gen_label(after_while_lbl)

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
            next_offset_before_statement = CG.next_offset

            # get the param's identifier and look it up
            identifier = token.lexeme
            Parser.error_on_variable_usage(identifier)
            er_lhs = Parser.s_table.find_in_all_scopes(identifier)

            Parser.match(token, TokenType.Identifier)

            if token.t_type == TokenType.AssignmentOperator:
                print(24, end=" ")
                Parser.match(token, TokenType.AssignmentOperator)
                er_rhs = Parser.expression(token)
                Parser.match(token, TokenType.Semicolon)
                CG.code_gen_assign(er_lhs, er_rhs)
            elif token.t_type == TokenType.OpenBracket:
                print(25, end=" ")
                Parser.match(token, TokenType.OpenBracket)
                er_subscript = Parser.expression(token)
                Parser.match(token, TokenType.CloseBracket)


                Parser.match(token, TokenType.AssignmentOperator)
                er_rhs = Parser.expression(token)
                Parser.match(token, TokenType.Semicolon)
                CG.code_gen_assign(er_lhs, er_rhs, dest_subscript=er_subscript)

            elif token.t_type == TokenType.OpenParen:
                print(26, end=" ")
                Parser.match(token, TokenType.OpenParen)
                param_list = Parser.expression_list(token)
                Parser.match(token, TokenType.CloseParen)
                Parser.match(token, TokenType.Semicolon)

                # First handle built-in functions
                if identifier in CG.BUILT_IN_FUNCTIONS.keys():
                    function, data_type = CG.BUILT_IN_FUNCTIONS[identifier]
                    function(data_type, param_list)

                else:
                    Parser.call_function(identifier, er_lhs, param_list)

            else:
                Parser.raise_production_not_found_error(
                    token, 'assignment_or_function_call')

            # Reclaim stack space that was used during this statement
            CG.next_offset = next_offset_before_statement
        else:
            Parser.raise_production_not_found_error(
                token, 'assignment_or_function_call')

    @staticmethod
    def expression(token):
        """
        Implements recursive descent for the rule:
        <expression> ==>
            35 <term> { TokenType.AddSubOperator <term> }
        :return:    an ExpressionRecord that holds the result of the expression
        """
        if token.t_type in (TokenType.OpenParen, TokenType.Identifier,
                            TokenType.Float, TokenType.Integer,
                            TokenType.String, TokenType.Char):
            print(35, end=" ")

            er_lhs = Parser.term(token)
            while token.t_type == TokenType.AddSubOperator:
                operator = token.lexeme
                Parser.match(token, TokenType.AddSubOperator)
                er_rhs = Parser.term(token)
                er_lhs = CG.gen_expression(er_lhs, er_rhs, operator)


            return er_lhs
        else:
            Parser.raise_production_not_found_error(token, 'expression')



    @staticmethod
    def term(token):
        """
        Implements recursive descent for the rule:
        <term> ==>
            39 <relfactor> { TokenType.MulDivModOperator <relfactor> }
        :return:    an ExpressionRecord that holds the result of the term
        """
        if token.t_type in (TokenType.OpenParen, TokenType.Identifier,
                            TokenType.Float, TokenType.Integer,
                            TokenType.String, TokenType.Char):
            print(39, end=" ")
            er_lhs = Parser.relfactor(token)
            while token.t_type == TokenType.MulDivModOperator:
                operator = token.lexeme
                Parser.match(token, TokenType.MulDivModOperator)
                er_rhs = Parser.relfactor(token)
                er_lhs = CG.gen_expression(er_lhs, er_rhs, operator)

            return er_lhs
        else:
            Parser.raise_production_not_found_error(token, 'term')



    @staticmethod
    def relfactor(token):
        """
        Implements recursive descent for the rule:
        <relfactor> ==>
            40 <factor> [TokenType.RelationalOperator <factor>]
        :return:    an ExpressionRecord that holds the result of the relfactor
        """
        if token.t_type in (TokenType.OpenParen, TokenType.Identifier,
                            TokenType.Float, TokenType.Integer,
                            TokenType.String, TokenType.Char):
            print(40, end=" ")
            er_lhs = Parser.factor(token)
            if token.t_type == TokenType.RelationalOperator:
                operator = token.lexeme
                Parser.match(token, TokenType.RelationalOperator)
                er_rhs = Parser.factor(token)
                return CG.gen_rel_expression(er_lhs, er_rhs, operator)
            return er_lhs
        else:
            Parser.raise_production_not_found_error(token, 'relfactor')



    @staticmethod
    def factor(token):
        """
        Implements recursive descent for the rule:
        <factor> ==>
            TokenType.OpenParen <expression> TokenType.CloseParen |
            <variable_or_function_call> |
            TokenType.Float |
            TokenType.Integer |
            TokenType.String
        :return:    an ExpressionRecord that holds the result of the factor
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

            return Parser.variable_or_function_call(token)

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
        :return:    an ExpressionRecord that holds the literal
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
            Parser.match(token, TokenType.Char)
        return er_literal



    @staticmethod
    def variable_or_function_call(token):
        """
        Implements recursive descent for the rule:
        <variable_or_function_call> ==>
            49 TokenType.Identifier TokenType.OpenBracket <expression>
                TokenType.CloseBracket |
            50 TokenType.OpenParen <expression_list> TokenType.CloseParen |
            51 TokenType.Identifier
        :return:    an ExpressionRecord that holds:
                    49 the value at array_id[subscript], if it was an array
                    50 the return value of the function, if it was a function;
                    51 the value of the variable, if it was a variable id
        """
        if token.t_type == TokenType.Identifier:
            identifier = token.lexeme
            exp_rec = Parser.s_table.find_in_all_scopes(identifier)

            Parser.match(token, TokenType.Identifier)

            if token.t_type == TokenType.OpenBracket:
                print(49, end=" ")
                Parser.match(token, TokenType.OpenBracket)
                er_subscript = Parser.expression(token)

                # Input validation: verify that the subscript is an integer,
                # and that exp_rec contains an array
                if er_subscript.data_type != DataTypes.INT:
                    raise SemanticError("Subscript is not an integer",
                                        Parser.file_reader.get_line_data())
                if not DataTypes.is_array(exp_rec.data_type):
                    raise SemanticError("Subscript applied to variable %s, "
                                        "which is not an array" % identifier,
                                        Parser.file_reader.get_line_data())

                # Match ]: wait until after potential error messages to do this
                Parser.match(token, TokenType.CloseBracket)

                # TODO: make this a function in CG
                # Make a temp ExpressionRecord to hold the value at
                # array[subscript], and return it
                result_exp_rec = ExpressionRecord(
                    DataTypes.array_to_basic(exp_rec.data_type),
                    CG.next_offset, is_temp=True, is_reference=False)
                CG.next_offset -= 4
                CG.code_gen_assign(result_exp_rec, exp_rec,
                                   src_subscript=er_subscript)
                return result_exp_rec

            elif token.t_type == TokenType.OpenParen:
                print(50, end=" ")
                if not isinstance(exp_rec, FunctionSignature) and \
                        not identifier in CG.BUILT_IN_FUNCTIONS.keys():
                    raise SemanticError("Tried to call %s as a function, "
                                        "but it was not a function." %
                                        identifier,
                                        Parser.file_reader.get_line_data())

                # exp_rec is actually a function signature, so call it that
                func_signature = exp_rec
                Parser.match(token, TokenType.OpenParen)
                er_params = Parser.expression_list(token)
                Parser.match(token, TokenType.CloseParen)

                return Parser.call_function(identifier, func_signature,
                                            er_params)

            else:
                print(51, end=" ")
                return exp_rec
        else:
            raise Parser.raise_production_not_found_error(
                token, "variable_or_function_call")



    @staticmethod
    def call_function(func_identifier, func_signature, er_params):
        """
        Handles built-in and user-defined function calls: checks that the
        callee is a function, checks that the parameters are of the right types,
        and tells the code generator to generate the function call.
        :param func_identifier:     The id of the function
        :param func_signature:      The FunctionSignature associated with the id
        :param er_params:           A list of ExpressionRecords that hold the
                                    parameters
        :return:                    An ExpressionRecord that holds the
                                    function's return value
        """
        # Handle built-in functions here:
        if func_identifier in CG.BUILT_IN_FUNCTIONS.keys():
            function, datatype = CG.BUILT_IN_FUNCTIONS[func_identifier]
            return function(datatype, er_params)

        # Input validation: verify that er_list types match the
        # function signature, and verify that the identifier is for a
        # function
        if not isinstance(func_signature, FunctionSignature):
            raise SemanticError("Tried to call %s(), but it wasn't a "
                                "function" % func_identifier,
                                Parser.file_reader.get_line_data())

        for i in range(len(func_signature.param_list_types)):
            expect_type = func_signature.param_list_types[i]
            if expect_type != er_params[i].data_type:
                raise SemanticError("Parameter for %s in position %d "
                                    "has the wrong type: expected %s" %
                                    (func_identifier, i, expect_type),
                                    Parser.file_reader)

        return CG.call_function(func_signature, er_params)



# If you execute "python3 ParserWithST.py", the program entry point is here:
# this code attempts to compile everything in the testCodeGen directory and
# puts all the output in the asmOutput directory

if __name__ == "__main__":
    test_file_dir = "/home/dave/PycharmProjects/Compiler/testCodeGen/"
    # "C:/Users/Dave/PycharmProjects/compiler/unusedTestPrograms/" #
    output_file_dir = "/home/dave/PycharmProjects/Compiler/asmOutput/"
    # "C:/Users/Dave/PycharmProjects/compiler/asmOutput/" #

    list_of_failed_compilations = []
    # For every file in the test file directory,
    for f in os.listdir(test_file_dir):
        success = False

        # Prepend the path of the test file directory
        input_filename = test_file_dir + f

        # Output filename: add extension .asm and put in output dir
        asm_out = output_file_dir + f + ".asm"
        # If there was an extension, replace it instead
        if '.' in f:
            asm_out = output_file_dir + '.'.join(f.split('.')[:-1]) + ".asm"

        print("\nParsing file " + f)

        try:
            success = Parser.parse(input_filename, asm_out)
        except Exception as ex:
            print('\n' + traceback.format_exc())
            # print("\nException occurred while parsing file %s:\n%s" % (f, ex))

        Parser.display_symbol_table()

        if not success:
            list_of_failed_compilations.append(f)
            os.remove(asm_out)
    if len(list_of_failed_compilations) > 0:
        print("The following files failed to compile:")
        for f in list_of_failed_compilations:
            print(f)
    else:
        print("All files compiled successfully!")

