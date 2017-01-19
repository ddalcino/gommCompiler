__author__ = 'dave'


class FileReader:
    """
    This class is used to hide the implementation of file reading behind an
    abstraction.
    """
    def __init__(self, filename):
        # Open file for reading
        self.file = open(filename, 'r')
        # The current line being processed
        self.current_line = self.file.readline()
        # The last line that was processed
        self.last_line = ""
        # The index into self.current_line that points to the current
        # character being processed
        self.current_line_index = 0



    def __enter__(self):
        """
        Allows 'with ... as ...' syntax, to ensure that files are closed
        when they are no longer needed
        """
        return self



    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Allows 'with ... as ...' syntax, to ensure that files are closed
        when they are no longer needed
        """
        self.file.close()



    def get_char(self):
        """
        Gets the next character available, and ensures that the next
        one will be available the next time it is called.
        :return:    The next character available, or None if at end of file
        """

        # If the current_line_index is positive, it refers to the current line
        if self.current_line_index >= 0:
            # If the current line is an empty line, we are at the end of the
            # file. Blank lines contain one character, '\n'
            if len(self.current_line) == 0:
                return None

            # Obtain the current character
            ch = self.current_line[self.current_line_index]
        else:
            # If the current_line_index is negative, it refers to the last line
            index = len(self.last_line) + self.current_line_index
            # Obtain the current character
            ch = self.last_line[index]

        # Increment the index, so the next time get_char is called, the next
        # char will be available
        self.current_line_index += 1

        # If we've gone past the end of the line, advance to the next line
        if self.current_line_index >= len(self.current_line):
            self.last_line = self.current_line
            self.current_line = self.file.readline()
            self.current_line_index = 0

        return ch



    def EOF(self):
        return self.current_line_index >= 0 and self.current_line == ""



    def put_back(self):
        """
        Points current_line_index back to the last character read, so that it
        may be read again.
        Does not support putting back more characters than exist on a single
        line, and will raise a FileReader.PutBackTooManyCharacters exception if
        this occurs.
        """
        self.current_line_index -= 1

        # Don't run off the end of self.last_line!
        if len(self.last_line) <= -self.current_line_index:
            raise FileReader.PutBackTooManyCharacters()



    class PutBackTooManyCharacters(Exception):
        """
        An empty class used as an exception, raised when the user calls
        put_back() more times than the FileReader can support
        """
        pass



class Scanner:

    def __init__(self):
        pass