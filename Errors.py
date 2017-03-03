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
    pass
