from Token import TokenType as tt, Keyword, Token

__author__ = 'dave'


grammar = {
    # grammar: a data structure that represents a complete grammar. The outer
    # structure is a dictionary; its keys represent non-terminal symbols,
    # and the values associated with those keys are a list of productions.

    # Each production is a list, in the form (number)(non-terminal|terminal)+
    # The number at the start of the list is an identifier, used to identify
    # particular productions; it is not part of any production.
    # A production could also be a None object instead of a list; this
    # designates an epsilon.

    # Each non-terminal symbol in a production is a string, which is the name
    # of that symbol.
    # Each terminal in a production is either a Token or a Token.TokenType
    # object. This is done to differentiate between different keywords;
    # conceivably, I could change every instance of a keyword into the
    # TokenType for a keyword, but I think that makes the grammar a lot less
    # useful and harder to read. Alternately, I could change each keyword
    # into its own TokenType.

    # A program is a list of function declarations
    "program": (
        (1, "function_decl", "program",),
        (2, None,),
    ),

    # A function declaration looks like:
    # func <id> (<param_list>) <ret_identifier> <ret_datatype> {<code_block>}
    "function_decl": (
        (3, Keyword.FUNC, tt.Identifier, tt.OpenParen, "param_list",
         tt.CloseParen, "return_identifier", "return_datatype", tt.OpenCurly,
         "statement_list", tt.CloseCurly,),
    ),

    # A parameter list is a list of basic declaration statements, of the form
    #  <identifier> <datatype>
    "param_list": (
        (4, tt.Identifier, "datatype", "remaining_param_list",),
        (5, None,),
    ),

    "remaining_param_list": (
        (6, tt.Comma, tt.Identifier, "datatype", "remaining_param_list",),
        (7, None,),        # an epsilon
    ),

    "datatype": (
        (8, Keyword.INT,),
        (9, Keyword.FLOAT,),
        (10, Keyword.CHAR,),
        (11, tt.OpenBracket, tt.Integer, tt.CloseBracket, "array_of_datatype",),
    ),

    "array_of_datatype": (
        (12, Keyword.INT,),
        (13, Keyword.FLOAT,),
        (14, Keyword.CHAR,),
    ),

    "return_identifier": (
        (15, tt.Identifier,),
    ),

    "return_datatype": (
        (16, "datatype",),
    ),

    # A statement list is a list of statements
    "statement_list": (
        (17, "basic_statement", "statement_list"),
        (18, None,),
    ),

    # A basic statement is in the form:
    # <statement> ::= <return_statement> | <if_statement> | <loop_statement> |
    # <declaration_statement> | <assignment_statement> |
    "basic_statement": (
        (19, Keyword.RETURN, tt.Semicolon),                 # return statement
        (20, Keyword.IF, "remaining_if_statement"),         # if statement
        (21, Keyword.WHILE, "remaining_while_statement"),   # loop statement
        # variable declaration statement
        (22, Keyword.VAR, tt.Identifier, "datatype", tt.Semicolon),
        # assignment or function call
        (23, tt.Identifier, "assignment_or_function_call", tt.Semicolon),
    ),

    "assignment_or_function_call": (
        (24, tt.AssignmentOperator, "expression"),        # assignment statement
        (25, tt.OpenBracket, "expression", tt.CloseBracket,  # array indexing
         tt.AssignmentOperator, "expression"),          # assignment statement
        (26, tt.OpenParen, "expression_list", tt.CloseParen),   # function call
    ),

    "expression_list": (
        (27, "expression", "remaining_expression_list"),
        (28, None,),
    ),
    "remaining_expression_list": (
        (29, tt.Comma, "expression", "remaining_expression_list",),
        (30, None,),
    ),

    "remaining_if_statement": (
        (31, tt.OpenParen, "boolean_expression", tt.CloseParen,
         tt.OpenCurly, "statement_list", tt.CloseCurly, "else_clause"),
    ),
    "else_clause": (
        (32, Keyword.ELSE, tt.OpenCurly, "statement_list", tt.CloseCurly,),
        (33, None,),
    ),

    "remaining_while_statement": (
        (34, tt.OpenParen, "boolean_expression", tt.CloseParen,
         tt.OpenCurly, "statement_list", tt.CloseCurly,),
    ),

    "expression": (
        (35, "term", "expr_prime"),
    ),
    "expr_prime": (
        (36, tt.AddSubOperator, "term", "expr_prime",),
        (37, tt.SubtractOperator, "term", "expr_prime",),
        (38, None,),
    ),
    "term": (
        (39, "factor", "term_prime"),
    ),
    "term_prime": (
        (40, tt.MulDivModOperator, "factor", "term_prime"),
        (41, tt.DivideOperator, "factor", "term_prime"),
        (42, tt.ModulusOperator, "factor", "term_prime"),
        (43, None,),
    ),
    "factor": (
        (44, tt.OpenParen, "expression", tt.CloseParen),
        (45, tt.Identifier, "variable_or_function_call"),
        (46, tt.Float,),
        (47, tt.Integer,),
        (48, tt.String,),
    ),
    "variable_or_function_call": (
        (49, tt.OpenBracket, "expression", tt.CloseBracket),    # array indexing
        (50, tt.OpenParen, "expression_list", tt.CloseParen),   # function call
        (51, None,),                            # epsilon, for variable
    ),

    "boolean_expression": (
        (52, "expression", "boolean_comparator", "expression",),
    ),
    "boolean_comparator": (
        (53, tt.EqualityOperator,),
        (54, tt.NotEqualOperator,),
        (55, tt.LessThanOperator,),
        (56, tt.LessThanOrEqualOp,),
    ),
}

g_keys = (
    'program', 'function_decl', 'param_list', 'remaining_param_list',
    'datatype', 'array_of_datatype', 'return_identifier', 'return_datatype',
    'statement_list', 'basic_statement', 'assignment_or_function_call',
    'expression_list', 'remaining_expression_list', 'remaining_if_statement',
    'else_clause', 'remaining_while_statement',
    'expression', 'expr_prime', 'term', 'term_prime', 'factor',
    'variable_or_function_call',
    'boolean_expression', 'boolean_comparator',
)

add_newline_before = (3, 17)

INDENT = "    "

def generate_parser():
    output_filename = "ParserGenerated.py"

    with open(output_filename, 'w') as file_out:
        INDENT + "\n    ".join(import_def.split('\n'))
        file_out.write(import_def)

        file_out.write("\n\n\nclass Parser:\n")
        class_comment = INDENT + '"""\n'+ INDENT + \
            'A static class, used to parse an input file into a parse tree.\n' \
            + INDENT + '"""\n'


        file_out.write(class_comment)
        for defn in (parser_def, match_def, token_is_in_terminals_def,
                     raise_error_def, error_def, ):
            file_out.write(INDENT + "\n    ".join(defn.split('\n')))

        for non_terminal in g_keys: # grammar.keys():
            file_out.write("\n\n\n%s@staticmethod\n%sdef %s(token, "
                           "file_reader):\n" % (
                INDENT, INDENT, non_terminal))
            file_out.write(grammar_to_comment(non_terminal))

            rule_set = grammar[non_terminal]

            is_first = True
            has_epsilon_rule = None in [x[1] for x in rule_set]
            in_if_statement = False

            for production in rule_set:
                line = ""
                expected = ""

                if production[1] is not None and \
                        not isinstance(production[1], str):
                    in_if_statement = True
                    # write keyword, if or elif
                    if is_first:
                        line = INDENT*2 + "if "
                        is_first = False
                    else:
                        line = INDENT*2 + "elif "

                    # write condition
                    if isinstance(production[1], tt):
                        expected = production[1]
                        line += "token.t_type == %s:\n" % expected

                    elif isinstance(production[1], Token):
                        expected = _keyword_names[production[1]]
                        line += "token.equals(%s):\n" % expected
                        # print(keyword_names[production[1]])

                    file_out.write(line)
                    # print rule
                    line = ""
                    if production[0] in add_newline_before:
                        line = INDENT*3 + "print(\"\")\n"
                    line += INDENT*3 + "print(%d, end=\" \")\n" % production[0]
                    file_out.write(line)
                    # match the token
                    line = INDENT*3 + "Parser.match(token, %s, " \
                                      "file_reader)\n" % \
                                      expected
                    file_out.write(line)
                    # print(line)

                    # match the rest of the tokens in the grammar
                    for symbol in production[2:]:

                        # print(str(symbol))
                        if isinstance(symbol, Token):
                            expected = _keyword_names[symbol]
                            line = INDENT*3+"Parser.match(token, %s, " \
                                             "file_reader)\n" % \
                                             expected
                        elif isinstance(symbol, str):
                            line = INDENT*3+"Parser.%s(token, file_reader)\n" % symbol
                        elif isinstance(symbol, tt):
                            expected = str(symbol)
                            line = INDENT*3+"Parser.match(token, %s, file_reader)\n" % expected
                            # print(keyword_names[symbol])
                            # print(symbol)
                        else:
                            line = INDENT*3+"pass\n"
                        file_out.write(line)
                        print(line)
                    print('\n')

                elif isinstance(production[1], str):
                    # Find out if rule-set contains an epsilon
                    has_epsilon = None in [x[1] for x in rule_set]

                    # check if first terminal is in FIRST()
                    first = [stringify_symbol(x) for x in
                             first_terminals(production[1])]

                    line = INDENT*2 + "if Parser.token_is_in(token, (%s)):\n" % \
                            ", ".join(first)
                    file_out.write(line)

                    line = ""
                    if production[0] in add_newline_before:
                        line = INDENT*3 + "print(\"\")\n"

                    line += INDENT*3+"print(%d, end=\" \")\n" % production[0]
                    file_out.write(line)

                    line = INDENT*3+"Parser.%s(token, file_reader)\n" % production[1]
                    file_out.write(line)
                    # match the rest of the tokens in the grammar
                    for symbol in production[2:]:

                        print(str(symbol))
                        if isinstance(symbol, Token):
                            expected = _keyword_names[symbol]
                            line = INDENT*3+"Parser.match(token, %s, " \
                                             "file_reader)\n" % \
                                             expected
                        elif isinstance(symbol, str):
                            line = INDENT*3+"Parser.%s(token, file_reader)\n" % symbol
                        elif isinstance(symbol, tt):
                            expected = str(symbol)
                            line = INDENT*3+"Parser.match(token, %s, file_reader)\n" \
                                   % expected
                            # print(keyword_names[symbol])
                            # print(symbol)
                        file_out.write(line)
                    if has_epsilon:
                        _id = [x[0] for x in rule_set if x[1] is None][0]
                        line = INDENT*2 + "else:\n" + \
                               INDENT*3 + "print(%d, end=\" \")\n" % _id
                        file_out.write(line)
                    else:
                        line = INDENT*2 + "else:\n" + \
                               INDENT*3 + "Parser.raise_production_not_found_error(token, '%s', " \
                                          "file_reader)\n" % non_terminal
                        file_out.write(line)
                # elif production[1] is None:       # it's an epsilon
                #     has_epsilon_rule = True
                #     line = INDENT + "else:\n" + \
                #         INDENT*2+"print(%d)\n" % production[0]
                #     file_out.write(line)
            if not has_epsilon_rule and in_if_statement:
                line = INDENT*2 + "else:\n" + INDENT*3 + \
                       "Parser.raise_production_not_found_error(token, '%s', file_reader)\n" % non_terminal
                file_out.write(line)
            elif in_if_statement:
                _id = [x[0] for x in rule_set if x[1] is None][0]
                line = INDENT*2 + "else:\n" + \
                       INDENT*3 + "print(%d, end=\" \")\n" % _id
                file_out.write(line)

        file_out.write(main_def)


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
        if production[1] is not None:
            # if the first symbol in the production is a non-terminal,
            if isinstance(production[1], str):
                # add all non-terminals for the production to first
                first.extend(first_terminals(production[1]))
            else:
                # otherwise, add a terminal symbol
                first.append(production[1])
        elif not skip_epsilon:
            # The list of productions includes an epsilon, so add a None
            # to the list
            first.append(None)
    return first


def grammar_to_comment(non_terminal):
    rule_set = grammar[non_terminal]
    return INDENT*2 + '"""\n' + \
        INDENT*2 + 'Implements recursive descent for the rule:\n' + \
        INDENT*2 + "<%s> ==> \n" % non_terminal + INDENT * 2 + \
        " |\n            ".join([production_to_str(x[1:]) for x in rule_set])\
            + '\n' + INDENT + '"""\n'


def production_to_str(production):
    return " ".join([stringify_symbol(x) for x in production])


token_is_in_terminals_def = """


def token_is_in(token, list_of_terminals):
    \"\"\"
    Checks to see if a token is present in a list of symbols
    \"\"\"
    try:
        for terminal in list_of_terminals:
            if token.equals(terminal) or token.t_type == terminal:
                return True
        return False
    except TypeError as e:
        terminal = list_of_terminals
        return token.equals(terminal) or token.t_type == terminal
"""

raise_error_def = """


def raise_production_not_found_error(current_token, non_terminal, file_reader):
    \"\"\"
    Gets data from the file reader and formats it as an error message
    \"\"\"
    line_data = file_reader.get_line_data()
    raise Parser.Error(
        "At line %d, column %d: " % (line_data["Line_Num"],
                                     line_data["Column"]) +
        "Could not find a production for terminal %r in non-terminal %s" %
        (current_token, non_terminal) +
        "\\n%s" % line_data["Line"] +
        " " * line_data["Column"] + "^\\n"
    )
"""


import_def = """
from Token import TokenType, Keyword, Token
from Scanner import Scanner
from FileReader import FileReader
from SymbolTable import SymbolTable
import os
"""

match_def = """


def match(current_token, expected, file_reader):
    \"\"\"
    Matches the current token with an expected token or token type,
    then reads the next token from the scanner.
    If a match cannot be made, raises a Parser.Error object.
    :param current_token:   The current token being read
    :param expected:        Either an expected Token (in the case of a
                            particular keyword) or a TokenType
    :param file_reader:     The FileReader from which to read the next token
    :return:                None
    \"\"\"
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
            "Tried to match %r with %r, but they were unequal.\\n" %
            (current_token, expected) +
            "%s" % line_data["Line"] +
            " " * line_data["Column"] + "^\\n"
        )

"""

error_def = """


class Error(Exception):
    \"\"\"
    An error that only the Parser can raise; used by match()
    \"\"\"
    pass

"""

parser_def = """


def parse(filename):
    \"\"\"
    Uses recursive descent to parse an input file, printing a list of
    productions as it goes. Opens the input file, and calls 'program()',
    which begins recursive descent until an EndOfFile token is reached.
    If no errors occur, it prints "Success!!!"
    :param filename:    The name of the file to parse.
    :return:            None
    \"\"\"
    with FileReader(filename) as fr:
        current_token = Scanner.get_token(fr)
        Parser.program(current_token, fr)
        Parser.match(current_token, TokenType.EndOfFile, fr)
        print("\\nSuccess!!!")
"""

main_def = """


test_file_dir = "/home/dave/PycharmProjects/Compiler/testParser/"

if __name__ == "__main__":
    # For every file in the test file directory,
    for f in os.listdir(test_file_dir):

        # Prepend the path of the test file directory
        input_filename = test_file_dir + f

        print("\\nParsing file " + f)

        try:
            Parser.parse(input_filename)
        except Exception as ex:
            print("\\nException occurred while parsing file %s:\\n%s" % (f, ex))
"""


def stringify_symbol(symbol):
    if symbol in _keyword_names.keys():
        return _keyword_names[symbol]
    elif isinstance(symbol, str):
        return "<%s>" % symbol
    elif symbol is None:
        return "<Epsilon>"
    else:
        return str(symbol)

keyword_names = {
    "if": "Keyword.IF",
    "else": "Keyword.ELSE",
    "while": "Keyword.WHILE",
    "func": "Keyword.FUNC",
    "return": "Keyword.RETURN",
    "int": "Keyword.INT",
    "float": "Keyword.FLOAT",
    "char": "Keyword.CHAR",
    "var": "Keyword.VAR",

}

_keyword_names = {
    Keyword.IF: "Keyword.IF",
    Keyword.ELSE: "Keyword.ELSE",
    Keyword.WHILE: "Keyword.WHILE",
    Keyword.FUNC: "Keyword.FUNC",
    Keyword.RETURN: "Keyword.RETURN",
    Keyword.INT: "Keyword.INT",
    Keyword.FLOAT: "Keyword.FLOAT",
    Keyword.CHAR: "Keyword.CHAR",
    Keyword.VAR: "Keyword.VAR",

}

if __name__ == "__main__":
    generate_parser()

    # for non_terminal in g_keys:
    #
    #     rule_set = grammar[non_terminal]
    #
    #     string= "<%s> ==> \n" % non_terminal + INDENT + \
    #         " |\n    ".join([production_to_str(x[0:]) for x in rule_set])
    #     print(string)
