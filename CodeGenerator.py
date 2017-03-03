from Token import Token, TokenType, DataTypes
from Errors import *


class ExpressionRecord:

    def __init__(self, data_type, loc):
        assert(isinstance(data_type, DataTypes))
        self.loc = loc
        self.data_type = data_type

    def __str__(self):
        return str(self.data_type).split('.')[-1] + " @%d" % self.loc


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
    # Data that models the current state of the Code Generator

    code_file = None        # A file to which the Code Generator will write
    is_code_ok = True       # Always True, unless errors have been encountered
    next_offset = 0         # The offset of the next available position on
                            # the stack
    num_labels_made = None

    #################################################################
    # STATIC CONSTANT DATA:

    MIPS_INST = {
        "+": {
            DataTypes.INT: "add",
            DataTypes.FLOAT: "add.s",
        },
        "-": {
            DataTypes.INT: "sub",
            DataTypes.FLOAT: "sub.s",
        },
        "*": {
            DataTypes.INT: "mul",
            DataTypes.FLOAT: "mul.s",
        },
        "/": {
            DataTypes.INT: "div",
            DataTypes.FLOAT: "div.s",
        },
        "%": {
            DataTypes.INT: "rem",
        },
    }

    MIPS_TYPES = {
        DataTypes.STRING: (".asciiz", '"%s"'),
        DataTypes.INT: (".word", '%d'),
        DataTypes.FLOAT: (".float", '%f'),
        DataTypes.CHAR: (".byte", '%c'),    #FIXME
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
               'ProgStart:\t.asciiz\t"Program Start\\n"\n' \
               'ProgEnd:\t.asciiz\t"Program End\\n"\n'

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
        CG.num_labels_made ={
            "string": 0,
            "float": 0,
            "function": 0,
        }



    @staticmethod
    def gen_string_label():
        label = "string_lbl_%d" % CG.num_labels_made["string"]
        CG.num_labels_made["string"] += 1
        return label


    @staticmethod
    def gen_float_label():
        label = "float_lbl_%d" % CG.num_labels_made["float"]
        CG.num_labels_made["float"] += 1
        return label



    @staticmethod
    def gen_function_label(function_id):
        label = "func_%d_%s" % (CG.num_labels_made["function"], function_id)
        CG.num_labels_made["function"] += 1
        return label



    @staticmethod
    def output(line_of_code):
        """
        Outputs a line of code to the code file, and adds an end of line character
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
        CG.output(CG.PROLOGUE)



    @staticmethod
    def write_epilogue():
        """
        Writes an epilogue to the asm file
        :return:
        """
        CG.output(CG.EPILOGUE)


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
        Turns an expression into code.
        :param erL:     An ExpressionRecord that defines the type and
                        location of the left side of the expression
        :param erR:     An ExpressionRecord that defines the type and
                        location of the right side of the expression
        :param operator:    A lexeme that defines the operation to be done
        :return:        An ExpressionRecord that defines where on the stack the
                        result has been stored
        """
        assert(isinstance(operator, str) and
               isinstance(erL, ExpressionRecord) and
               isinstance(erR, ExpressionRecord))

        if erL.data_type != erR.data_type:
            raise SemanticError("Left expression is not the same type as "
                                   "right expression.")
        if operator not in CG.MIPS_INST.keys() or \
                erL.data_type not in CG.MIPS_INST[operator].keys():
            raise SemanticError(
                "Unsupported operation: %s on values of type %r." %
                (operator, erL.data_type))

        er_result = ExpressionRecord(erL.data_type, CG.next_offset)
        instruction = CG.MIPS_INST[operator][erL.data_type]

        if er_result.data_type == DataTypes.INT:

            CG.code_gen("lw", "$t0", "%d($sp)" % erL.loc)
            CG.code_gen("lw", "$t1", "%d($sp)" % erR.loc)
            CG.code_gen(instruction, "$t0", "$t0", "$t1")
            CG.code_gen("sw", "$t0", "%d($sp)" % CG.next_offset)
            CG.next_offset -= 4
            return er_result

        elif er_result.data_type == DataTypes.FLOAT:

            CG.code_gen("lwc1", "$f0", "%d($sp)" % erL.loc)
            CG.code_gen("lwc1", "$f1", "%d($sp)" % erR.loc)
            CG.code_gen(instruction, "$f0", "$f0", "$f1")
            CG.code_gen("swc1", "$f0", "%d($sp)" % CG.next_offset)
            CG.next_offset -= 4
            return er_result



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

        if rd is None:
            line_of_code = "\t%s\t\t\t%s" % (instruction, f_comment)
        elif rt is None:
            line_of_code = "\t%s\t%s\t%s" % (instruction, rd, f_comment)
        elif rs is None:
            line_of_code = "\t%s\t%s,%s\t%s" % (instruction, rd, rt, f_comment)
        else:
            line_of_code = "\t%s\t%s,%s,%s\t%s" % \
                           (instruction, rd, rt, rs, f_comment)
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



    @staticmethod
    def gen_labelled_data(label, data_type, value):
        """
        Prints a comment on its own line of code.
        :param comment:     The comment to print
        """
        CG.output(".data")
        CG.output(label + ":\t" + CG.MIPS_TYPES[data_type][0] + "\t" +
                  CG.MIPS_TYPES[data_type][1] % value)
        CG.output(".text")



    @staticmethod
    def declare_variable(data_type, identifier, size=1):
        """
        Reserves space on the stack for a variable.
        :param data_type:   A Token.DataTypes object
        :param identifier:  The variable's id (for comment)
        :param size:
        :return:
        """
        var = ExpressionRecord(data_type=data_type, loc=CG.next_offset)
        CG.next_offset -= 4*size
        CG.code_gen_comment("Space reserved on stack for var %s at %d($sp)" %
                            (identifier, var.loc))
        return var


    @staticmethod
    def create_literal(data_type, value):
        """
        Creates a literal and puts it on the stack. Ints and chars are loaded as
        immediates, within the instruction; floats are added to labels and
        then loaded into the stack. Strings are written in code, associated
        with a label, and then a pointer to the string is stored on the stack.
        :param data_type:    A DataTypes object (an enum defined in Token)
        :param value:   The value to be stored on the stack
        :return:        An ExpressionRecord that contains the type and
                        stack offset that defines where the literal exists
        """
        assert(isinstance(data_type, DataTypes))
        literal = ExpressionRecord(data_type=data_type, loc=CG.next_offset)
        CG.next_offset -= 4
        if data_type == DataTypes.INT:
            CG.code_gen("li", "$t0", value)
            CG.code_gen("sw", "$t0", "%d($sp)" % literal.loc)
        elif data_type == DataTypes.CHAR:
            CG.code_gen("li", "$t0", ord(value))
            CG.code_gen("sw", "$t0", "%d($sp)" % literal.loc)
        elif data_type == DataTypes.FLOAT:
            # make a label
            label = CG.gen_float_label()
            # put value into code, at that label
            CG.gen_labelled_data(label, data_type, value)
            CG.code_gen("la", "$t0", label)     # load address of float
            CG.code_gen("lw", "$t0", "($t0)")   # store float in $t0
            # store float on stack
            CG.code_gen("sw", "$t0", "%d($sp)" % literal.loc)
        elif data_type == DataTypes.STRING:
            label = CG.gen_string_label()
            CG.gen_labelled_data(label, data_type, value)
            CG.code_gen("la", "$t0", label)
            # store pointer to string on the stack
            CG.code_gen("sw", "$t0", "%d($sp)" % literal.loc)
        return literal


    @staticmethod
    def code_gen_assign(er_lhs, er_rhs):
        assert(isinstance(er_lhs, ExpressionRecord) and
               isinstance(er_rhs, ExpressionRecord))

        if er_lhs.data_type != er_rhs.data_type:
            raise SemanticError("Left hand side is not the same type as "
                                "the right hand side.")

        if er_lhs.data_type == DataTypes.INT:
            CG.code_gen("lw", "$t0", "%d($sp)" % er_rhs.loc)
            CG.code_gen("sw", "$t0", "%d($sp)" % er_lhs.loc)
        elif er_lhs.data_type == DataTypes.FLOAT:
            CG.code_gen("lwc1", "$f0", "%d($sp)" % er_rhs.loc)
            CG.code_gen("swc1", "$f0", "%d($sp)" % er_lhs.loc)




    @staticmethod
    def array_subscript_to_stack_entry(er_array, er_subscript):
        """
        Returns the expression record for er_array[er_subscript]
        :param er_array:    The ExpressionRecord for an array
        :param er_subscript: The subscript into that array
        :return: the expression record for er_array[er_subscript]
        """

        # We want to generate this code:
        # lw $t0,er_subscript.loc($sp)  #puts the subscript in t0
        # addi $t0,$t0,er_array.loc     #t0 has the offset of desired location
        # add $t0,$t0,$sp               #t0 has the address of desired location
        # lw $t0,($t0)                  #t0 has the value at the desired loc
        # sw $t0,
        pass



    #################################################################
    # BUILT_IN FUNCTIONS
    #     print,
    #     read_int,
    #     read_float,
    #     read_char

    @staticmethod
    def gen_print(exp_rec):
        """
        Generates inline code that calls the syscall for the appropriate
        print function
        :param exp_rec:     the ExpressionRecord that holds the value we want
                            to print
        """
        assert(isinstance(exp_rec, ExpressionRecord))
        if exp_rec.data_type == DataTypes.INT:
            CG.code_gen("lw", "$a0", "%d($sp)" % exp_rec.loc,
                        comment="Move int to a0")
            CG.code_gen("li", "$v0", 1, comment="Syscall for print_int")
            CG.code_gen("syscall")
        elif exp_rec.data_type == DataTypes.FLOAT:
            CG.code_gen("lwc1", "$f0", "%d($sp)" % exp_rec.loc,
                        comment="Move float to f0")
            CG.code_gen("li", "$v0", 2, comment="Syscall for print_float")
            CG.code_gen("syscall")
        elif exp_rec.data_type == DataTypes.CHAR:
            CG.code_gen("lw", "$a0", "%d($sp)" % exp_rec.loc,
                        comment="Move char to a0")
            CG.code_gen("li", "$v0", 11, comment="Syscall for print_char")
            CG.code_gen("syscall")
        elif exp_rec.data_type == DataTypes.STRING:
            CG.code_gen("lw", "$a0", "%d($sp)" % exp_rec.loc,
                        comment="Move string address to a0")
            CG.code_gen("li", "$v0", 4, comment="Syscall for print_string")
            CG.code_gen("syscall")
        else:
            raise SemanticError("Unsupported argument for print()")


    @staticmethod
    def gen_read_int(exp_rec):
        """
        Generates code that calls the read_int syscall.
        :param exp_rec: the ExpressionRecord in which to store the result
        """

        CG.code_gen("li", "$v0", 5, comment="Syscall for read_int")
        CG.code_gen("syscall")
        CG.code_gen("sw", "$v0", "%d($sp)" % exp_rec.loc)



    @staticmethod
    def gen_read_float(exp_rec):
        """
        Generates code that calls the read_float syscall.
        :param exp_rec: the ExpressionRecord in which to store the result
        """

        CG.code_gen("li", "$v0", 6, comment="Syscall for read_float")
        CG.code_gen("syscall")
        CG.code_gen("swc1", "$f0", "%d($sp)" % exp_rec.loc)



    @staticmethod
    def gen_read_int(exp_rec):
        """
        Generates code that calls the read_char syscall.
        :param exp_rec: the ExpressionRecord in which to store the result
        """

        CG.code_gen("li", "$v0", 12, comment="Syscall for read_char")
        CG.code_gen("syscall")
        CG.code_gen("sw", "$v0", "%d($sp)" % exp_rec.loc)



    @staticmethod
    def call_function(func_rec, params):
        """
        Generates code within a function that prepares for and calls another
        function.
        :param func_rec:    The ExpressionRecord for the function to call
        :param params:      A list of ExpressionRecords for the paramaters to
                            send to the function
        :return:            An ExpressionRecord that holds the return value
        """

        # Reserve space on the stack for the return value

        # Calculate the distance from the


