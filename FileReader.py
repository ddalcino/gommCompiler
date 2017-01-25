# Filename: FileReader.py
# David Dalcino
# CS 6110
# Prof. Reiter
# Winter 2017
# CSU East Bay
#
# Scanner Assignment
# Due 1/26/17


class FileReader:
    """
    This class is used to hide the implementation of file reading behind an
    abstraction. Please instantiate using 'with ... as' syntax, like this:
        with FileReader.FileReader(filename) as file_reader:
            file_reader.get_char()
            # ...
    """
    def __init__(self, filename):
        """
        Constructor for FileReader.
        :param filename:    The name of the file to open
        :return:            FileReader object
        """
        # The name of the file to open
        self.filename = filename
        # Open file pointer; should be populated by using 'with ... as'
        # syntax to ensure that files are closed automatically when they are
        # no longer needed
        self.file = None
        # The current line being processed
        self.current_line = ""
        # The last line that was processed
        self.last_line = ""
        # The index into self.current_line that points to the current
        # character being processed
        self.current_line_index = 0
        # The line number of the current line.
        self.current_line_number = 0



    def __enter__(self):
        """
        Opens the file referred to by self.filename, and fills the line buffer,
        self.current_line, with the first line of the file
        Allows 'with ... as ...' syntax, to ensure that files are closed
        when they are no longer needed
        """
        # Open file for reading
        self.file = open(self.filename, 'r')
        # Fill the current_line buffer
        self.fill_buffer()
        return self



    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Ensures that files are closed when they are no longer needed. Called
        automatically when a 'with ... as' block is exited.
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
            # Fill the current_line buffer, updating self accordingly
            self.fill_buffer()

        return ch



    def fill_buffer(self):
        """
        Moves the current_line into the last_line buffer, and reads the next
        line into current_line.
        Will set current_line to "" if at EOF.
        Also ensures that current_line_index and current_line_number agree with
        the new state of current_line.
        :return:    None
        """
        # hang on to the last line, in case we need to back up
        self.last_line = self.current_line

        # if self.file.readline() returns "", we are at end of file
        self.current_line = self.file.readline()
        self.current_line_index = 0
        self.current_line_number += 1



    def EOF(self):
        # if self.file.readline() returns "", we are at end of file
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



    def get_line_data(self):
        """
        :return:    A dict containing the line number, column, and line for the
                    character that would next be returned by get_char(); if
                    you want the data for the last character you saw,
                    call put_back() first.
        """
        if self.current_line_index < 0:
            return {
                "Line_Num": self.current_line_number - 1,
                "Column": len(self.last_line) + self.current_line_index,
                "Line": self.last_line
            }
        else:
            return {
                "Line_Num": self.current_line_number,
                "Column": self.current_line_index,
                "Line": self.current_line
            }



    class PutBackTooManyCharacters(Exception):
        """
        An empty class used as an exception, raised when the user calls
        put_back() more times than the FileReader can support
        """
        pass
