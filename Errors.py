from ParserWithST import Parser

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


class SemanticError(Exception):
    def __init__(self, message):
        line_data = Parser.file_reader.get_line_data()
        full_msg = \
            "At line %d, column %d: " % (line_data["Line_Num"],
                                         line_data["Column"]) + \
            message + \
            "\n%s" % line_data["Line"] + \
            " " * line_data["Column"] + "^\n"
        Exception.__init__(self, message)


