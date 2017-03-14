"""
Filename: Errors.py
Tested with Python 3.5.1

David Dalcino
CS 6110
Prof. Reiter
Winter 2017
CSU East Bay

This file defines some error classes, which inherit from the base class
ParseError. ParseError inherits from Exception. In this way, parts of the
parser and code generator that need to report errors can raise one of these
exceptions
"""

#################################################################
# ERROR CLASSES

class ParseError(Exception):
    """
    An error that only the Parser can raise; a parent class for
    RedeclaredVariableError, UseUndeclaredVariableError, MatchError, and
    ProductionNotFoundError
    """
    pass



class RedeclaredVariableError(ParseError):
    """
    An error that only the Parser can raise; used by error_on_variable_usage()
    """
    pass



class UseUndeclaredVariableError(ParseError):
    """
    An error that only the Parser can raise; used by error_on_variable_usage()
    """
    pass



class MatchError(ParseError):
    """
    An error that only the Parser can raise; used by match()
    """
    pass



class ProductionNotFoundError(ParseError):
    """
    An error that only the Parser can raise; used by
    raise_production_not_found_error()
    """
    pass


class SemanticError(ParseError):
    """
    A semantic error, raised by the Parser or Code Generator.
    """
    def __init__(self, message, line_data):
        """
        Constructs an error.
        :param message:     A descriptive error message
        :param line_data:   a dictionary that holds information about the
                            current line being processed. Should be populated
                            by FileReader.get_line_data()
        """
        full_msg = \
            "At line %d, column %d: " % (line_data["Line_Num"],
                                         line_data["Column"]) + \
            message + \
            "\n%s" % line_data["Line"] + \
            " " * line_data["Column"] + "^\n"
        Exception.__init__(self, full_msg)


