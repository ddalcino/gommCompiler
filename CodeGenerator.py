from Token import TokenType, DataTypes
from Errors import *


class ExpressionRecord:

    def __init__(self, data_type, loc, is_temp, is_reference=False):
        """

        :param data_type:   A Token.DataTypes object. INT|FLOAT|CHAR|STRING
        :param loc:         The offset from $sp where the value exists
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
        self.loc = loc
        self.data_type = data_type
        self.is_temp = is_temp
        self.is_ref = is_reference

    def __str__(self):
        return str(self.data_type).split('.')[-1] + " @%d" % self.loc



class FunctionSignature:
    def __init__(self, identifier, label=None,
                 #param_list_ids,
                 param_list_types=None,
                 #return_id,
                 return_type=None):
        #assert(len(param_list_types) == len(param_list_ids))
        # for type in param_list_types:
        #     assert(isinstance(type, DataTypes))
        # assert(isinstance(return_type, DataTypes))

        self.identifier = identifier
        self.label = label
        #self.param_list_ids = param_list_ids
        self.param_list_types = param_list_types
        #self.return_id = return_id
        self.return_type = return_type

    def __str__(self):
        params_str = ', '.join(
            [str(x).split('.')[-1] for x in self.param_list_types])
        return_type_str = str(self.return_type).split('.')[-1]
        return self.identifier + "(" + params_str + ") " + return_type_str


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
    next_offset = -8         # The offset of the next available position on
                            # the stack
    num_labels_made = None
    source_file_reader = None

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
            DataTypes.INT: "div",
        },
    }

    MIPS_TYPES = {
        DataTypes.STRING: (".asciiz", '%s'),
        DataTypes.INT: (".word", '%d'),
        DataTypes.FLOAT: (".float", '%f'),
        DataTypes.CHAR: (".byte", '%c'),    #FIXME
    }

    BUILT_IN_FUNCTIONS = {}

    PROLOGUE = '\t.text\n' \
               '\t.globl main\n' \
               'main:\n' \
               '\tmove\t$fp,$sp\n' \
               '\tla\t$a0,ProgStart\n' \
               '\tli\t$v0,4                    # Print Syscall\n' \
               '\tsyscall\n' \
               '\tjal\tmain_func\n'

    EPILOGUE = '\tla $a0,ProgEnd\n' \
               '\tli $v0,4                    # Print Syscall\n' \
               '\tsyscall\n' \
               '\tli $v0,10                   # Exit Syscall\n' \
               '\tsyscall\n' \
               '\t.data\n' \
               'ProgStart:\t.asciiz\t"Program Start\\n"\n' \
               'ProgEnd:\t.asciiz\t"Program End\\n"\n' \
               '\t.text\n'

    LINE_ENDING = "\n"                  # "\r\n" for windows


    #################################################################
    # STATIC MEMBER FUNCTIONS:



    @staticmethod
    def init(code_file, source_file_reader):
        """
        Initializes the Code Generator, so that it will be ready to write a
        code file.
        :param code_file:   A file object that the user has opened with the
                            builtin Python 'open' command. Must be writable.
        """
        assert(code_file.writable())
        CG.code_file = code_file
        CG.is_code_ok = True
        CG.next_offset = -8
        CG.num_labels_made ={
            "string": 0,
            "float": 0,
            "function": 0,
            "else": 0,
            "after_else": 0,
            "while": 0,
        }
        CG.BUILT_IN_FUNCTIONS = {
            "print": CG.gen_print,
            "read_int": CG.gen_read_int,
            "read_float": CG.gen_read_float,
            "read_char": CG.gen_read_char,
        }
        CG.source_file_reader = source_file_reader



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
    def gen_else_label():
        label = "else_lbl_%d" % CG.num_labels_made["else"]
        CG.num_labels_made["else"] += 1
        return label



    @staticmethod
    def gen_after_else_label():
        label = "after_else_lbl_%d" % CG.num_labels_made["after_else"]
        CG.num_labels_made["after_else"] += 1
        return label



    @staticmethod
    def gen_while_labels():
        before_label = "while_lbl_%d" % CG.num_labels_made["while"]
        after_label = "after_while_lbl_%d" % CG.num_labels_made["while"]
        CG.num_labels_made["while"] += 1
        return before_label, after_label



    @staticmethod
    def gen_function_label(function_id):
        if function_id == "main":
            return "main_func"
        else:
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

        # In new function, return var is at 4($fp),
        # params are at 8($fp) thru (4*len(params)+8)($fp)

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
        #     '\tsw\t$ra, %d($fp)\n' % (stack_entry_size-4) +\
        #     '\tsw\t$fp, %d($fp)\n' % (stack_entry_size-8) +\
        #     '\taddiu\t$fp, $sp, %d\n' % stack_entry_size
        #
        # # Restore return address, frame pointer, stack pointer, and return
        # function_epilogue = \
        #     '\tlw\t$ra, %d($fp)\n' % (stack_entry_size-4) +\
        #     '\tlw\t$fp, %d($fp)\n' % (stack_entry_size-8) +\
        #     '\taddiu\t$sp, $sp, %d\n' % stack_entry_size +\
        #     '\tjr\t$ra\n'


    @staticmethod
    def gen_expression(er_lhs, er_rhs, operator):
        """
        Turns an expression into code.
        :param er_lhs:  An ExpressionRecord that defines the type and
                        location of the left side of the expression
        :param er_rhs:     An ExpressionRecord that defines the type and
                        location of the right side of the expression
        :param operator:    A lexeme that defines the operation to be done
        :return:        An ExpressionRecord that defines where on the stack the
                        result has been stored
        """
        assert(isinstance(operator, str) and
               isinstance(er_lhs, ExpressionRecord) and
               isinstance(er_rhs, ExpressionRecord))

        if er_lhs.data_type != er_rhs.data_type:
            raise SemanticError("Left expression is not the same type as "
                                "right expression.",
                                CG.source_file_reader.get_line_data())
        if operator not in CG.MIPS_INST.keys() or \
                er_lhs.data_type not in CG.MIPS_INST[operator].keys():
            raise SemanticError(
                "Unsupported operation: %s on values of type %r." %
                (operator, er_lhs.data_type),
                CG.source_file_reader.get_line_data())

        # Can we overwrite er_lhs?
        if er_lhs.is_temp:
            # Reuse the same stack entry
            er_result = er_lhs
        elif er_rhs.is_temp:
            # Reuse the rhs entry instead
            er_result = er_rhs
        else:
            # Make a new stack entry
            er_result = CG.create_temp(er_lhs.data_type)

        instruction = CG.MIPS_INST[operator][er_lhs.data_type]

        if er_result.data_type == DataTypes.INT:

            CG.code_gen("lw", "$t0", "%d($fp)" % er_lhs.loc)
            CG.code_gen("lw", "$t1", "%d($fp)" % er_rhs.loc)
            CG.code_gen(instruction, "$t0", "$t0", "$t1")

            # Mod needs an extra instruction: move result from HI register to t0
            if operator == "%":
                CG.code_gen("mfhi", "$t0", comment="Modulus: remainder is in "
                                                   "HI register")

            CG.code_gen("sw", "$t0", "%d($fp)" % er_result.loc)
            return er_result

        elif er_result.data_type == DataTypes.FLOAT:

            CG.code_gen("lwc1", "$f0", "%d($fp)" % er_lhs.loc)
            CG.code_gen("lwc1", "$f1", "%d($fp)" % er_rhs.loc)
            CG.code_gen(instruction, "$f0", "$f0", "$f1")
            CG.code_gen("swc1", "$f0", "%d($fp)" % er_result.loc)
            return er_result
        # TODO: handle else



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

        line_of_code = label + ":\t\t\t" + f_comment
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
        Prints data with a label, between lines of code
        """
        CG.output("")
        CG.output("\t.data")
        CG.output(label + ":\t" + CG.MIPS_TYPES[data_type][0] + "\t" +
                  CG.MIPS_TYPES[data_type][1] % value)
        CG.output("")
        CG.output("\t.text")



    @staticmethod
    def declare_variable(data_type, identifier, size=1):
        """
        Reserves space on the stack for a variable.
        :param data_type:   A Token.DataTypes object
        :param identifier:  The variable's id (for comment)
        :param size:        Number of bytes to reserve
        :return:
        """
        var = ExpressionRecord(data_type=data_type, loc=CG.next_offset,
                               is_temp=False)
        CG.next_offset -= 4*size
        # CG.code_gen("addi", "$sp", "$sp", -4*size,
        CG.code_gen_comment(comment="Reserve %d words on stack for var %s at"
                                    " %d($fp)" % (size, identifier, var.loc))
        return var


    @staticmethod
    def push_var(source_exp_rec):
        """
        Pushes a copy of a variable on the stack
        :param source_exp_rec:   ExpressionRecord for the variable to push
        """
        var = ExpressionRecord(data_type=source_exp_rec.data_type,
                               loc=CG.next_offset, is_temp=False)
        CG.next_offset -= 4
        # CG.code_gen("addi", "$sp", "$sp", -4,
        CG.code_gen_comment(comment="Reserve a word on stack for param at "
                                    "%d($fp)" % var.loc)
        CG.code_gen_assign(var, source_exp_rec)



    @staticmethod
    def create_temp(data_type):
        """
        Reserves one word on the stack for a temp variable, and returns an
        ExpressionRecord for it
        :param data_type:   A Token.DataTypes object
        :return:            ExpressionRecord that holds the temp variable
        """
        temp_var = ExpressionRecord(data_type=data_type, loc=CG.next_offset,
                                    is_temp=True)
        CG.next_offset -= 4
        # CG.code_gen("addi", "$sp", "$sp", -4,
        CG.code_gen_comment(comment="Reserved one word on stack for temp var "
                                    "%d($fp)" % temp_var.loc)
        return temp_var


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

        # make space on stack for literal
        literal = CG.create_temp(data_type)

        if data_type == DataTypes.INT:
            CG.code_gen("li", "$t0", value)
            CG.code_gen("sw", "$t0", "%d($fp)" % literal.loc)
        elif data_type == DataTypes.CHAR:
            CG.code_gen("li", "$t0", ord(value))
            CG.code_gen("sw", "$t0", "%d($fp)" % literal.loc)
        elif data_type == DataTypes.FLOAT:
            # make a label
            label = CG.gen_float_label()
            # put value into code, at that label
            CG.gen_labelled_data(label, data_type, value)
            CG.code_gen("la", "$t0", label)     # load address of float
            CG.code_gen("lw", "$t0", "($t0)")   # store float in $t0
            # store float on stack
            CG.code_gen("sw", "$t0", "%d($fp)" % literal.loc)
        elif data_type == DataTypes.STRING:
            label = CG.gen_string_label()
            CG.gen_labelled_data(label, data_type, value)
            CG.code_gen("la", "$t0", label)
            # store pointer to string on the stack
            CG.code_gen("sw", "$t0", "%d($fp)" % literal.loc)
        return literal



    @staticmethod
    def code_gen_assign(er_lhs, er_rhs):
        assert(isinstance(er_lhs, ExpressionRecord) and
               isinstance(er_rhs, ExpressionRecord))

        if er_lhs.data_type != er_rhs.data_type:
            raise SemanticError("Left hand side is not the same type as "
                                "the right hand side.",
                                CG.source_file_reader.get_line_data())

        if er_lhs.data_type == DataTypes.INT:
            CG.code_gen("lw", "$t0", "%d($fp)" % er_rhs.loc)
            CG.code_gen("sw", "$t0", "%d($fp)" % er_lhs.loc)
        elif er_lhs.data_type == DataTypes.FLOAT:
            CG.code_gen("lwc1", "$f0", "%d($fp)" % er_rhs.loc)
            CG.code_gen("swc1", "$f0", "%d($fp)" % er_lhs.loc)



    @staticmethod
    def code_gen_if(er_lhs, operator, er_rhs, lbl_on_failed_test):

        if operator == TokenType.EqualityOperator:
            CG.code_gen("lw", "$t0", "%d($fp)" % er_lhs.loc)
            CG.code_gen("lw", "$t1", "%d($fp)" % er_rhs.loc)
            CG.code_gen("bne", "$t0", "$t1", lbl_on_failed_test)
            pass
        elif operator == TokenType.NotEqualOperator:
            CG.code_gen("lw", "$t0", "%d($fp)" % er_lhs.loc)
            CG.code_gen("lw", "$t1", "%d($fp)" % er_rhs.loc)
            CG.code_gen("beq", "$t0", "$t1", lbl_on_failed_test)
        elif operator == TokenType.LessThanOrEqualOp:
            CG.code_gen("lw", "$t0", "%d($fp)" % er_lhs.loc)
            CG.code_gen("lw", "$t1", "%d($fp)" % er_rhs.loc)
            CG.code_gen("sub", "$t0", "$t0", "$t1", comment="t0=t0-t1")
            CG.code_gen("bgtz", "$t0", lbl_on_failed_test)
        elif operator == TokenType.LessThanOperator:
            CG.code_gen("lw", "$t0", "%d($fp)" % er_lhs.loc)
            CG.code_gen("lw", "$t1", "%d($fp)" % er_rhs.loc)
            CG.code_gen("sub", "$t0", "$t0", "$t1", comment="t0=t0-t1")
            CG.code_gen("bgez", "$t0", lbl_on_failed_test)



    @staticmethod
    def assign_to_array_entry(er_array, er_subscript, er_rhs):
        """
        :param er_array:        The ExpressionRecord for an array
        :param er_subscript:    The subscript into that array
        :param er_rhs:        The ExpressionRecord to copy into array[subscript]
        """

        # We want to generate this code:
        # lw $t1,er_rhs.loc($fp)        #put rhs value in t1
        # lw $t0,er_subscript.loc($fp)  #puts the subscript in t0
        # addi $t0,$t0,er_array.loc     #t0 has the offset of desired location
        # add $t0,$t0,$sp               #t0 has the address of desired location
        # sw $t1,($t0)                  #store rhs in desired location
        CG.code_gen("lw", "$t0", "%d($fp)" % er_subscript.loc,
                    comment="put subscript in t0")
        # multiply subscript by 4
        CG.code_gen("sll", "$t0", "$t0", 2, comment="multiply subscript by 4")
        # offset of destination, from $sp, is er_array.loc - t0
        CG.code_gen("li", "$t1", er_array.loc)
        CG.code_gen("sub", "$t0", "$t1", "$t0",
                    comment="offset of destination is array_location - t0")
        CG.code_gen("add", "$t0", "$t0", "$fp",
                    comment="calculate address of destination")
        CG.code_gen("lw", "$t1", "%d($fp)" % er_rhs.loc,
                    comment="put rhs value in t1")
        CG.code_gen("sw", "$t1", "($t0)", comment="store rhs in destination")



    @staticmethod
    def array_entry_to_temp_val(er_array, er_subscript):
        """
        Copies an array entry into a temp ExpressionRecord on the stack
        :param er_array:        The ExpressionRecord for an array
        :param er_subscript:    The subscript into that array
        :return:                A temporary ExpressionRecord, holds value at
                                er_array[er_subscript]
        """
        # make space to hold temp value
        exp_rec = CG.create_temp(DataTypes.array_to_basic(er_array.data_type))

        CG.code_gen("lw", "$t0", "%d($fp)" % er_subscript.loc,
                    comment="put subscript in t0")
        # multiply subscript by 4
        CG.code_gen("sll", "$t0", "$t0", 2, comment="multiply subscript by 4")
        # offset of source, from $sp, is er_array.loc - t0
        CG.code_gen("li", "$t1", er_array.loc)
        CG.code_gen("sub", "$t0", "$t1", "$t0",
                    comment="offset of source is array_location - t0")
        CG.code_gen("add", "$t0", "$t0", "$fp",
                    comment="calculate address of source")
        CG.code_gen("lw", "$t0", "($t0)", comment="Dereference t0")
        CG.code_gen("sw", "$t0", "%d($fp)" % exp_rec.loc,
                    comment="store value on stack")
        return exp_rec



    @staticmethod
    def gen_print(exp_rec_list):
        """
        Generates inline code that calls the syscall for the appropriate
        print function
        :param exp_rec_list:   the ExpressionRecord that holds the value we want
                            to print
        """
        assert(len(exp_rec_list) == 1)
        exp_rec = exp_rec_list[0]
        assert(isinstance(exp_rec, ExpressionRecord))
        if exp_rec.data_type == DataTypes.INT:
            CG.code_gen("lw", "$a0", "%d($fp)" % exp_rec.loc,
                        comment="Move int to a0")
            CG.code_gen("li", "$v0", 1, comment="Syscall for print_int")
            CG.code_gen("syscall")
        elif exp_rec.data_type == DataTypes.FLOAT:
            CG.code_gen("lwc1", "$f12", "%d($fp)" % exp_rec.loc,
                        comment="Move float to f12")
            CG.code_gen("li", "$v0", 2, comment="Syscall for print_float")
            CG.code_gen("syscall")
        elif exp_rec.data_type == DataTypes.CHAR:
            CG.code_gen("lw", "$a0", "%d($fp)" % exp_rec.loc,
                        comment="Move char to a0")
            CG.code_gen("li", "$v0", 11, comment="Syscall for print_char")
            CG.code_gen("syscall")
        elif exp_rec.data_type == DataTypes.STRING:
            CG.code_gen("lw", "$a0", "%d($fp)" % exp_rec.loc,
                        comment="Move string address to a0")
            CG.code_gen("li", "$v0", 4, comment="Syscall for print_string")
            CG.code_gen("syscall")
        else:
            raise SemanticError("Unsupported argument for print()",
                                CG.source_file_reader.get_line_data())



    @staticmethod
    def gen_read_int():
        """
        Generates code that calls the read_int syscall.
        """
        # Make a temp ExpressionRecord to hold the result
        exp_rec = CG.create_temp(DataTypes.INT)

        CG.code_gen("li", "$v0", 5, comment="Syscall for read_int")
        CG.code_gen("syscall")
        CG.code_gen("sw", "$v0", "%d($fp)" % exp_rec.loc)
        return exp_rec



    @staticmethod
    def gen_read_float():
        """
        Generates code that calls the read_float syscall.
        """

        # Make a temp ExpressionRecord to hold the result
        exp_rec = CG.create_temp(DataTypes.FLOAT)

        CG.code_gen("li", "$v0", 6, comment="Syscall for read_float")
        CG.code_gen("syscall")
        CG.code_gen("swc1", "$f0", "%d($fp)" % exp_rec.loc)
        return exp_rec



    @staticmethod
    def gen_read_char():
        """
        Generates code that calls the read_char syscall.
        """

        # Make a temp ExpressionRecord to hold the result
        exp_rec = CG.create_temp(DataTypes.CHAR)

        CG.code_gen("li", "$v0", 12, comment="Syscall for read_char")
        CG.code_gen("syscall")
        CG.code_gen("sw", "$v0", "%d($fp)" % exp_rec.loc)
        return exp_rec



    @staticmethod
    def call_function(func_rec, params):
        """
        Generates code within a function that prepares for and calls another
        function.
        :param func_rec:    The ExpressionRecord for the function to call
        :param params:      A list of ExpressionRecords for the parameters to
                            send to the function
        :return:            An ExpressionRecord that holds the return value
        """
        assert(isinstance(func_rec, FunctionSignature))

        # store links and saved status
        # store temporaries and local data
        # store parameters and returned value
        er_retval = CG.declare_variable(func_rec.return_type, "return_var", 1)
        for er_param in params:
            # push param val on stack
            CG.push_var(er_param)

        # In new function, return var is at (4*len(params)+8)($fp),
        # params are at 4($fp) thru (4*len(params)+4)($fp)


        # We know that the sp should be at CG.next_offset from fp
        CG.code_gen("addi", "$sp", "$fp", CG.next_offset)

        # store control link and return address
        # CG.code_gen("addi", "$sp", "$sp", -4)
        CG.code_gen("sw", "$fp", "($sp)", comment="store old control link")

        CG.code_gen("move", "$fp", "$sp", comment="make new control link")
        CG.code_gen("addi", "$sp", "$sp", -4)
        CG.code_gen("sw", "$ra", "($sp)", comment="store return address")

        # call the function
        CG.code_gen("jal", func_rec.label)

        # restore control link and return address
        #ra=-4($fp)
        #sp = fp
        #fp=0(fp)
        CG.code_gen("lw", "$ra", "-4($fp)", comment="restore old ra")
        CG.code_gen("move", "$sp", "$fp", comment="restore old sp")
        CG.code_gen("addi", "$sp", "$sp", 4*(len(params)+1),
                    comment="remove params and control link from stack")
        CG.code_gen("lw", "$fp", "($fp)", comment="restore old fp")

        return er_retval


