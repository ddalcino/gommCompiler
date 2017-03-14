"""
Filename: SymbolTable.py
Tested using Python 3.5.1

David Dalcino
CS 6110
Prof. Reiter
Winter 2017
CSU East Bay

Symbol Table Assignment Due 1/14/17

This file defines a SymbolTable, which is organized into several scopes,
each of which hold a list of variable and function identifiers; these
variables and functions are only visible while they are in an open scope.

Each variable identifier is attached to an ExpressionRecord that defines its
relative physical location in memory, datatype, etc. ExpressionRecords are
defined in ExpressionRecord.py.

Each function identifier is attached to a FunctionSignature that defines the
order and types of parameters, the return type, and a label to which a caller
must jump and link. FunctionSignatures are defined in ExpressionRecord.py.
Because functions can only be declared in the global scope, FunctionSignatures
are only found in the global scope. Also, variables cannot be declared in the
global scope, so the only key-value pairs in the global scope are
function_identifier-FunctionSignature pairs.
"""

from ExpressionRecord import FunctionSignature


class Scope:
    """
    This is a wrapper class that contains a Python primitive dict object. The
    only functionality that it adds is the ability to hold an id number than
    can be held outside the dict; this keeps track of the scope number.
    """
    def __init__(self, id_number):
        """
        Constructor; makes a new Scope
        :param id_number:   the scope number
        """
        self.id_number = id_number
        self.data = {}



    def find(self, key):
        """ Finds a key in the dict """
        return self.data[key]



    def contains(self, key):
        """ Finds out if a key exists in the dict """
        return key in self.data



    def insert(self, key, value):
        """ Inserts a key value pair in the dict """
        self.data[key] = value



    def __str__(self):
        """ returns a string representation of the scope """
        return "Scope %d:\n" % self.id_number + \
               ", ".join("[%s]=%s" % (key, self.data[key])
                         for key in sorted(self.data.keys())) + '\n'



class SymbolTable:
    """
    SymbolTable is a class meant to be used in a compiler. It keeps track of
    symbols in code, and what scope they are in, and it can be used to store
    other metadata regarding these symbols. It supports the actions 'insert,'
    'find,' 'find_in_all_scopes,' and 'display.'
    """

    # Builtin functions; should be visible everywhere
    builtin_functions = {
        "print": {},
        "read_int": {},
        "read_float": {},
        "read_char": {},
        "cast_int": {},
        "cast_float": {},
        "cast_char": {},
    }



    def __init__(self):
        # an array of Scopes; each Scope represents an open scope
        self.open_scopes = []
        # an array of Scopes; each Scope represents an open scope
        self.closed_scopes = []
        # the total number of scopes that have been opened
        self.scope_count = 0

        # Get the symbol table ready to accept new values: open a new scope.
        # This is the global scope; closing it is an error
        self.open_scope()



    def insert(self, key, value):
        """
        Inserts a new key-value pair into the symbol table. Does not permit
        insertion if the key already exists in the table.
        :param key:     a string: the identifier that the symbol refers to
        :param value:   any metadata attached to the identifier
        :return:        True if the insert occurred properly; false if not.
        """

        # Disallow insertion to a scope that already has the key,
        # or if it's a built in function
        if self.open_scopes[-1].contains(key) or \
                        key in SymbolTable.builtin_functions.keys():
            return False

        # Perform the insertion
        self.open_scopes[-1].insert(key, value)



    def find(self, key):
        """
        Finds a symbol in the current scope
        :param key:     a string: the identifier to be found
        :return:        the value associated with the identifier, or None if
                        the key doesn't exist in the current scope
        """
        # if it's a built-in function,
        if key in SymbolTable.builtin_functions.keys():
            return SymbolTable.builtin_functions[key]
        if self.open_scopes[-1].contains(key):
            # Return the associated value, if the key exists in the scope
            return self.open_scopes[-1].find(key)
        # If the key isn't found, return None
        return None



    def find_in_all_scopes(self, key):
        """
        Finds a symbol, if it exists, in all open scopes. If it exists in
        multiple open scopes, it will choose the occurrence in the innermost
        open scope, nearest to the last scope opened.
        :param key:     a string: the identifier to be found
        :return:        the value associated with the identifier, or None if
                        the key doesn't exist in any open scope
        """
        # if it's a built-in function,
        if key in SymbolTable.builtin_functions.keys():
            return SymbolTable.builtin_functions[key]
        # Traverse the open scopes in reverse order
        for i in range(len(self.open_scopes)-1, -1, -1):
            if self.open_scopes[i].contains(key):
                # Return the associated value, if the key exists in the scope
                return self.open_scopes[i].find(key)
        # If the key isn't found, return None
        return None



    def display(self):
        """ Prints the contents of the SymbolTable """
        print("Open Scopes: %d exist\n" % len(self.open_scopes))
        for scope in self.open_scopes:
            # print each open scope
            print("============================================")
            print(str(scope))
        print("Closed Scopes: %d exist\n" % len(self.closed_scopes))
        for scope in self.closed_scopes:
            # print each closed scope
            print("============================================")
            print(str(scope))



    def open_scope(self):
        """ Opens a new scope and increments the scope count """
        self.open_scopes.append(Scope(self.scope_count))
        self.scope_count += 1



    def close_scope(self):
        """
        Closes the current scope and moves it to the list of closed scopes
        """

        # We should not be allowed to close the global scope; this should be
        # an error
        if len(self.open_scopes) == 1:
            raise SymbolTable.CloseGlobalScopeException()

        # Keep the closed scope in the list of closed scopes
        self.closed_scopes.append(self.open_scopes[-1])
        # Remove the closed scope from the list of open scopes
        self.open_scopes.pop()



    def get_scope_id(self):
        """ Returns the number associated with the innermost open scope """
        return self.open_scopes[-1].id_number



    def get_undefined_prototypes(self):
        """
        Searches for FunctionSignatures in the symbol table that have not yet
        been defined. If any are found, it returns a list of their identifiers.
        """
        undef_func_ids = []     # a list to hold the identifiers for
                                # undefined functions

        # Only the global scope can hold FunctionSignatures
        scope = self.open_scopes[0]
        for func_id in scope.data.keys():       # Look at all items in scope
            func_signature = scope.data[func_id]
            if isinstance(func_signature, FunctionSignature):
                if func_signature.is_prototype:
                    # Any time a function is defined, is_prototype is set
                    # to False, therefore if is_prototype is True, then
                    # it hasn't been defined
                    undef_func_ids.append(func_signature.identifier)
        return undef_func_ids


    class CloseGlobalScopeException(Exception):
        """
        An empty class used to denote that a user attempted to close the global
        scope. This should not be allowed to occur, but the user should be
        able to recover from the error, so this class is necessary.
        """
        pass
