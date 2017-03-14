"""
Filename: ExpressionRecord.py
Tested using Python 3.5.1

David Dalcino
CS 6110
Prof. Reiter
Winter 2017
CSU East Bay

This file defines ExpressionRecords, FunctionSignatures, and DataTypes.
"""


from enum import Enum


class ExpressionRecord:
    """
    ExpressionRecord keeps track of variables and temporary values held on
    the stack. Each ExpressionRecord has a physical location on the stack.
    Variables have ExpressionRecords that are stored in the symbol table.
    """

    def __init__(self, data_type, loc, is_temp, is_reference=False):
        """

        :param data_type:   A Token.DataTypes object. INT|FLOAT|CHAR|STRING|BOOL
        :param loc:         The offset from $fp where the value exists
        :param is_temp:     A boolean to let us know if the record is
                            temporary, and may be overwritten when no longer
                            in use. Always False for variables; True for
                            anything else
        :param is_reference: A boolean, lets us know if the value is a
                            reference or not, and will need to be
                            dereferenced before use
        :return:
        """
        assert(isinstance(data_type, DataTypes))
        self.loc = loc              # The location of the value on the stack,
                                    # measured in bytes above or below $fp
        self.data_type = data_type  # The data type of the value
        self.is_temp = is_temp      # Boolean; if true, the value may be
                                    # thrown away after being used
        self.is_ref = is_reference  # Boolean; if true, the value stored at
                                    # loc($fp) is a pointer to somewhere else in
                                    # the stack, and will need to be
                                    # dereferenced before being used



    def is_array(self):
        """
        :return:    a bool that tells you if this is an array or not
        """
        return DataTypes.is_array(self.data_type)



    def __str__(self):
        """ String representation that tells location and datatype """
        return str(self.data_type).split('.')[-1] + " @%d" % self.loc



class FunctionSignature:
    """
    A FunctionSignature serves to keep track of a function's identifier,
    return type, and the datatypes that it requires as arguments and their
    order. They also keep track of whether the function has actually been
    defined yet, or if only the prototype has been declared. If a
    prototype has been declared, then later on the function must be
    defined, and its signature must agree with the existing prototype.

    FunctionSignatures are stored in the SymbolTable, associated with
    function identifiers. Because functions can only be declared in the
    global scope, FunctionSignatures are only found in the global scope.
    """
    def __init__(self, identifier, label=None,
                 param_list_types=None,
                 return_type=None,
                 is_prototype=False):

        self.identifier = identifier        # The name of the function
        self.label = label                  # The label where it starts
        self.param_list_types = param_list_types    # Parameter types & order
        self.return_type = return_type      # The return type
        self.is_prototype = is_prototype    # If true, it was forward
                                            # declared and not yet defined;
                                            # otherwise, it was defined already.



    def __str__(self):
        """ String representation of FunctionSignature """
        params_str = ', '.join(
            [str(x).split('.')[-1] for x in self.param_list_types])
        return_type_str = str(self.return_type).split('.')[-1]

        return self.identifier + "(" + params_str + ") " + return_type_str



class DataTypes(Enum):
    """ An enumeration for basic datatypes """
    INT = 1
    FLOAT = 2
    CHAR = 3
    STRING = 4
    BOOL = 5            # not yet declarable; BOOL is for internal use only
                        # for conditional expressions
    ARRAY_INT = 6
    ARRAY_FLOAT = 7
    ARRAY_CHAR = 8
    ARRAY_STRING = 9
    ARRAY_BOOL = 10



    @staticmethod
    def basic_to_array(data_type):
        """ Turns a basic data type into an array type """
        mapping = {
            DataTypes.INT:      DataTypes.ARRAY_INT,
            DataTypes.FLOAT:    DataTypes.ARRAY_FLOAT,
            DataTypes.CHAR:     DataTypes.ARRAY_CHAR,
            DataTypes.STRING:   DataTypes.ARRAY_STRING,
            DataTypes.BOOL:     DataTypes.ARRAY_BOOL,
        }
        return mapping[data_type]



    @staticmethod
    def is_array(data_type):
        """ Tells you if a datatype is an array type or not """
        return data_type in (DataTypes.ARRAY_INT, DataTypes.ARRAY_FLOAT,
                             DataTypes.ARRAY_CHAR, DataTypes.ARRAY_STRING,
                             DataTypes.ARRAY_BOOL)


    @staticmethod
    def array_to_basic(data_type):
        """ Turns an array data type into a basic type """
        mapping = {
            DataTypes.ARRAY_INT:    DataTypes.INT,
            DataTypes.ARRAY_FLOAT:  DataTypes.FLOAT,
            DataTypes.ARRAY_CHAR:   DataTypes.CHAR,
            DataTypes.ARRAY_STRING: DataTypes.STRING,
            DataTypes.ARRAY_BOOL:   DataTypes.BOOL,
        }
        return mapping[data_type]