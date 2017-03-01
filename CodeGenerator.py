from Token import Token, TokenType
from enum import Enum


class ExpressionRecord:

    def __init__(self, type):
        assert(type == TokenType.Integer or type == TokenType.Float or
               type == TokenType.Char or type == TokenType.String)
        self.loc = 0
        self.type = type


class CG:
    """
    CG: short for Code Generator
    This is a singleton implementation of a Code Generator; I have chosen the
    singleton pattern because I don't think it makes any sense to have more
    than one Code Generator, and I need to keep some internal state associated
    with the Code Generator that I would prefer not to be global.
    """

    #################################################################
    # STATIC DATA MEMBERS:
    # Data that models th current state of the Code Generator

    code_file = None        # A file to which the Code Generator will write
    is_code_ok = True       # Always True, unless errors have been encountered
    next_offset = 0         # The offset of the next available position on
                            # the stack

    #################################################################
    # STATIC CONSTANT DATA:

    MIP_INST = {
        "+": {
            TokenType.Integer: "add",
            TokenType.Float: "add.s",
        },
        "-": {
            TokenType.Integer: "sub",
            TokenType.Float: "sub.s",
        },
        "*": {
            TokenType.Integer: "mul",
            TokenType.Float: "mul.s",
        },
        "/": {
            TokenType.Integer: "div",
            TokenType.Float: "div.s",
        },
        "%": {
            TokenType.Integer: "rem",
        },
    }

    PROLOGUE = '\t.text\n' \
               '\t.globl main\n' \
               'main:\n' \
               '\tmove\t$fp $sp\n' \
               '\tla $a0 ProgStart\n' \
               '\tli $v0 4                    # Print Syscall\n' \
               '\tsyscall\n'

    EPILOGUE = '\tla $a0 ProgEnd\n' \
               '\tli $v0 4                    # Print Syscall\n' \
               '\tsyscall\n' \
               '\tli $v0 10                   # Exit Syscall\n' \
               '\tsyscall\n' \
               '\t.data\n' \
               'ProgStart:\t.asciiz\t"Program Start\n"' \
               'ProgEnd:\t.asciiz\t"Program End\n"'

    LINE_ENDING = "\n"                  # "\r\n" for windows

    #################################################################
    # STATIC MEMBER FUNCTIONS:



    @staticmethod
    def init(code_file):
        """
        Initializes the Code Generator, so that it will be ready to write a
        code file.
        :param code_file:   A file object that the user has opened with the
                            builtin Python 'open' command. Must be writable.
        """
        assert(code_file.writable())
        CG.code_file = code_file
        CG.is_code_ok = True
        CG.next_offset = 0



    @staticmethod
    def output(line_of_code):
        """
        Outputs a line of code to the code file.
        :param line_of_code:    A line of code to write
        """
        CG.code_file.write(line_of_code + CG.LINE_ENDING)
        # print(line_of_code)




    @staticmethod
    def write_prolog():
        """
        Writes a prologue to the asm file
        :return:
        """
        pass

    @staticmethod
    def write_epilogue():
        """
        Writes an epilogue to the asm file
        :return:
        """


    @staticmethod
    def write_function(identifier, param_list):
        """

        :return:
        """

        # Use param_list to decide how large to make the stack:
        # Assume that each parameter is 4 bytes
        # Add an extra 8 bytes for the return address and frame pointer
        stack_entry_size = 4 * (len(param_list) + 2)

        # # The index of the function
        # index = len(self.functions)
        #
        # # The name of the function
        # function_name = "function_%d" % index
        # self.functions[identifier]={
        #     "asm_name": function_name,
        #     "param_list": param_list
        # }
        #
        # # Write the function label and open the stack frame
        # function_prologue = \
        #     '%s:\n' % function_name + \
        #     '\taddiu\t$sp, $sp, -%d\n' % stack_entry_size + \
        #     '\tsw\t$ra, %d($sp)\n' % (stack_entry_size-4) +\
        #     '\tsw\t$fp, %d($sp)\n' % (stack_entry_size-8) +\
        #     '\taddiu\t$fp, $sp, %d\n' % stack_entry_size
        #
        # # Restore return address, frame pointer, stack pointer, and return
        # function_epilogue = \
        #     '\tlw\t$ra, %d($sp)\n' % (stack_entry_size-4) +\
        #     '\tlw\t$fp, %d($sp)\n' % (stack_entry_size-8) +\
        #     '\taddiu\t$sp, $sp, %d\n' % stack_entry_size +\
        #     '\tjr\t$ra\n'


    @staticmethod
    def gen_expression(erL, erR, operator):
        """

        :param erL:
        :param erR:
        :param operator:
        :return:
        """
        assert(isinstance(operator, Token))
        assert(isinstance(erL, ExpressionRecord))
        assert(isinstance(erR, ExpressionRecord))

        if erL.type != erR.type:
            raise CG.SemanticError("Left expression is not the "
                                              "same type as right expression.")
        else:
            if operator.lexeme not in CG.MIP_INST.keys() or \
                    erL.type not in CG.MIP_INST[
                        operator.lexeme].keys():
                raise CG.SemanticError(
                    "Unsupported operation: %s on values of type %r." %
                    (operator.lexeme, erL.type))

            instruction = CG.MIP_INST[operator.lexeme][erL.type]
            if erL.type == TokenType.Integer:

                CG.code_gen("lw", "$t0", "%d($sp)" % erL.loc)
                CG.code_gen("lw", "$t1", "%d($sp)" % erR.loc)
                CG.code_gen(instruction, "$t0", "$t0", "$t1")
                CG.code_gen("sw", "$t0", "%d($sp)" % CG.next_offset)
                CG.next_offset -= 4

            elif erL.type == TokenType.Float:

                CG.code_gen("lwc1", "$f0", "%d($sp)" % erL.loc)
                CG.code_gen("lwc1", "$f1", "%d($sp)" % erR.loc)
                CG.code_gen(instruction, "$f0", "$f0", "$f1")
                CG.code_gen("swc1", "$f0", "%d($sp)" % CG.next_offset)
                CG.next_offset -= 4



    @staticmethod
    def code_gen(instruction, rd=None, rt=None, rs=None, comment=None):
        """
        Generates a line of code, and inserts it into the code file.

        :param instruction: The MIPS instruction to use
        :param rd:      The destination register
        :param rt:      The temp register (optional)
        :param rs:      The source register (optional)
        :param comment: Any comment to be added on this line of code
        :return:        None
        """
        # TODO: insert line_of_code into the code file instead of print

        f_comment = ""          # Formatted comment
        if comment is not None:
            f_comment = "# " + comment


        if rt is None:
            line_of_code = "\t%s\t%s\t%s" % instruction, rd, f_comment
        elif rs is None:
            line_of_code = "\t%s\t%s,%s\t%s" % instruction, rd, rt, f_comment
        else:
            line_of_code = "\t%s\t%s,%s,%s\t%s" % instruction, rd, rt, rs, \
                           f_comment
        CG.output(line_of_code)



    @staticmethod
    def code_gen_label(label, comment=None):
        """
        Prints a label, with a comment if available
        :param label:       The label to print
        :param comment:     The comment to print. Optional
        """

        f_comment = ""          # Formatted comment
        if comment is not None:
            f_comment = "# " + comment

        line_of_code = label + "\t\t\t" + f_comment
        CG.output(line_of_code)



    @staticmethod
    def code_gen_comment(comment):
        """
        Prints a comment on its own line of code.
        :param comment:     The comment to print
        """
        line_of_code = "\t\t\t\t# " + comment
        CG.output(line_of_code)



    class SemanticError(Exception):
        pass




