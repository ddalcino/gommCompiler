__author__ = 'dave'


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

        # Disallow insertion to a scope that already has the key
        if self.open_scopes[-1].contains(key):
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
        # Traverse the open scopes in reverse order
        for i in range(len(self.open_scopes)-1, -1, -1):
            if self.open_scopes[i].contains(key):
                # Return the associated value, if the key exists in the scope
                return self.open_scopes[i][key]
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
        return self.open_scopes[-1].id_number



    class CloseGlobalScopeException(Exception):
        """
        An empty class used to denote that a user attempted to close the global
        scope. This should not be allowed to occur, but the user should be
        able to recover from the error, so this class is necessary.
        """
        pass
