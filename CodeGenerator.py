"""
Filename: CodeGenerator.py
Tested using Python 3.5.1

David Dalcino
CS 6110
Prof. Reiter
Winter 2017
CSU East Bay

This file contains CG, a class that implements a code generator for MIPS.
This file is separate from the parser, in an attempt to keep code generation
separate; theoretically, if you wanted to compile to some architecture other
than MIPS, you would only have to rewrite this file and not the parser. I am
not convinced that the parser is entirely separate from the MIPS
architecture, but I have done the best I can.
"""

from ExpressionRecord import ExpressionRecord, FunctionSignature, DataTypes
from Errors import *


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
    next_offset = -8        # The offset of the next available position on
                            # the stack
    num_labels_made = None      # A dictionary that keeps track of how many
                                # labels were made of each type
    source_file_reader = None   # A FileReader that contains the source code.
                                # Used only for error messages.
    last_instruction = None     # A record of the last instruction generated,
                                # for use in peephole optimization. Only
                                # accessed or written to by CG.code_gen().

    #################################################################
    # STATIC CONSTANT DATA:

    # MIPS_INST defines what MIPS instructions should be used for each
    # arithmetic operator. It uses nested dictionaries, where the outer key
    # is an arithmetic operator, and the inner key is a datatype. An
    # instruction would be accessed by CG.MIPS_INST[operator][datatype].
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

    # MIPS_TYPES is a dictionary that defines how literals should be written
    # into an assembly file when they are attached to a label. The key is a
    # datatype, and the associated value is a tuple of the form
    # (TYPE, FORMAT_STRING) where TYPE is the datatype that the MIPS
    # assembler expects, and FORMAT_STRING is used to translate from a Python
    # datatype into a literal that the assembler can understand.
    MIPS_TYPES = {
        DataTypes.STRING: (".asciiz", '%s'),
        DataTypes.INT: (".word", '%d'),
        DataTypes.FLOAT: (".float", '%f'),
        DataTypes.CHAR: (".byte", '%c'),
    }

    # BUILT_IN_FUNCTIONS will be a dictionary that pairs the identifiers of
    # built-in functions with the functions in CG that will implement them.
    # Python refuses to make key-value pairs between a key and a function
    # here, before those functions have been defined, so I have make the
    # actual dictionary in the CG.init() function below, which must be called
    # before CG is used for anything else.
    BUILT_IN_FUNCTIONS = {}


    # Not sure if this is really necessary, but I'm using it anyway just in
    # case this code ever has to be run on a Windows machine. Any time CG
    # executes a write to the .asm output file, it ends the line with one of
    # these.
    LINE_ENDING = "\n"                  # "\r\n" for windows


    # A label used as the program entry point. The prologue jumps to this
    # label, and when the CG.gen_label() is asked to create a label for the
    # main function, it returns this label.
    ENTRY_POINT_LABEL = "main_func"


    # The pro-log
    PROLOGUE = '\t.text' + LINE_ENDING + \
               '\t.globl main' + LINE_ENDING + \
               'main:' + LINE_ENDING + \
               '\tmove\t$fp,$sp' + LINE_ENDING + \
               '\tla\t$a0,ProgStart' + LINE_ENDING + \
               '\tli\t$v0,4                   # Print Syscall' + LINE_ENDING + \
               '\tsyscall' + LINE_ENDING + \
               '\tjal\t' + ENTRY_POINT_LABEL + LINE_ENDING


    # The post-log
    EPILOGUE = '\tla $a0,ProgEnd' + LINE_ENDING + \
               '\tli $v0,4                    # Print Syscall' + LINE_ENDING + \
               '\tsyscall' + LINE_ENDING + \
               '\tli $v0,10                   # Exit Syscall' + LINE_ENDING + \
               '\tsyscall' + LINE_ENDING + \
               '\t.data' + LINE_ENDING + \
               'ProgStart:\t.asciiz\t"Program Start\\n"' + LINE_ENDING + \
               'ProgEnd:\t.asciiz\t"Program End\\n"' + LINE_ENDING + \
               '\t.text' + LINE_ENDING


    #################################################################
    # STATIC MEMBER FUNCTIONS:

    @staticmethod
    def init(code_file, source_file_reader):
        """
        Initializes the Code Generator, so that it will be ready to write a
        code file. This function must be run before using CG for anything else.
        :param code_file:   A file object that the user has opened with the
                            builtin Python 'open' command. Must be writable.
        :param source_file_reader:  A FileReader that is being used to read
                                    the source code file. Used only for
                                    printing errors.
        """
        assert(code_file.writable())
        CG.code_file = code_file
        CG.is_code_ok = True
        CG.next_offset = -8
        CG.num_labels_made = {
            "string": 0,
            "float": 0,
            "function": 0,
            "else": 0,
            "after_else": 0,
            "while": 0,
        }
        CG.BUILT_IN_FUNCTIONS = {
            "print":        (CG.gen_print, None),
            "read_int":     (CG.gen_read, DataTypes.INT),
            "read_float":   (CG.gen_read, DataTypes.FLOAT),
            "read_char":    (CG.gen_read, DataTypes.CHAR),
            "cast_int":     (CG.gen_cast, DataTypes.INT),
            "cast_float":   (CG.gen_cast, DataTypes.FLOAT),
            # "cast_char":    (CG.gen_cast, DataTypes.CHAR), # Planned for later
        }
        CG.source_file_reader = source_file_reader



    @staticmethod
    def gen_label(type):
        """
        Generates two labels, with a unique number attached to them,
        and keeps track of how many of that type have been made.
        :param type:    A string; must be in ("string","float","else","while")
        :return:        Two labels that look like: TYPE_lbl_N, after_TYPE_lbl_N,
                        where TYPE is the parameter type, and N is the number of
                        labels that have been made of that type. The 'after'
                        labels will only be useful for the 'else' and 'while'
                        types, but they will be made for the others to keep
                        things simple.
        """
        if type in ("string", "float", "else", "while"):
            label = "%s_lbl_%d" % (type, CG.num_labels_made[type])
            after_label = "after_%s_lbl_%d" % \
                          (type, CG.num_labels_made[type])
            CG.num_labels_made[type] += 1
            return label, after_label
        else:
            print("\nProgrammer error; gen_label() only supports labels of "
                  "types string, float, else, and while")
            assert False



    @staticmethod
    def gen_function_label(function_id):
        """
        Makes a unique label for each function.
        :param function_id:     the function identifier
        :return:                a label that looks like func_ID_N, where ID
                                is the identifier, and N is the number of
                                function labels that have been made so far.
                                If function_id is 'main', then the unique
                                program entry point label is returned; it is
                                hard-coded to be CG.ENTRY_POINT_LABEL because
                                the prologue is hard-coded to jump to it.
        """
        if function_id == "main":
            return CG.ENTRY_POINT_LABEL
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

            CG.load_reg("$t0", er_lhs, "$t1")
            CG.load_reg("$t1", er_rhs, "$t2")
            CG.code_gen(instruction, "$t0", "$t0", "$t1")

            # Mod needs an extra instruction: move result from HI register to t0
            if operator == "%":
                CG.code_gen("mfhi", "$t0", comment="Modulus: remainder is in "
                                                   "HI register")

            CG.store_reg(er_result, reg_src="$t0", reg_temp="$t1",
                         reg_temp2="$t2")
            return er_result

        elif er_result.data_type == DataTypes.FLOAT:

            CG.load_reg("$f0", er_lhs, "$t1", use_coprocessor_1=True)
            CG.load_reg("$f1", er_rhs, "$t2", use_coprocessor_1=True)
            CG.code_gen(instruction, "$f0", "$f0", "$f1")
            CG.store_reg(er_result, reg_src="$f0", reg_temp="$t0",
                         reg_temp2="$t1", use_coprocessor_1=True)
            return er_result
        raise SemanticError(
            "Unsupported operation: %s on values of type %r." %
            (operator, er_lhs.data_type),
            CG.source_file_reader.get_line_data())



    @staticmethod
    def gen_rel_expression(er_lhs, er_rhs, operator):
        """
        Generates an ExpressionRecord of type BOOL
        :param er_lhs:
        :param er_rhs:
        :param operator:
        :return:
        """
        assert  isinstance(er_lhs, ExpressionRecord) and \
                isinstance(er_rhs, ExpressionRecord)
        if er_lhs.data_type != er_rhs.data_type:
            raise SemanticError("Types must match to use relational operator",
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

        if er_lhs.data_type == DataTypes.BOOL:
            # put lhs in t0 and rhs in t1
            CG.load_reg(reg_dest="$t0", er_src=er_lhs, reg_temp="$t2")
            CG.load_reg(reg_dest="$t1", er_src=er_rhs, reg_temp="$t2")

            if operator == "&&":
                CG.code_gen("beq", "$t0", "$0", "1f")
                CG.code_gen("beq", "$t1", "$0", "1f")
                CG.code_gen("li", "$t0", 1, comment="Test was true")
                CG.code_gen("b", "2f")
                CG.code_gen_label("1", comment="Failed test")
                CG.code_gen("li", "$t0", 0, comment="Test was false")
                CG.code_gen_label("2")
                CG.store_reg(er_result, "$t0", "$t1", "$t2")
            elif operator == "||":
                CG.code_gen("bne", "$t0", "$0", "1f")
                CG.code_gen("bne", "$t1", "$0", "1f")
                CG.code_gen("li", "$t0", 0, comment="Test was false")
                CG.code_gen("b", "2f")
                CG.code_gen_label("1", comment="Passed test")
                CG.code_gen("li", "$t0", 1, comment="Test was true")
                CG.code_gen_label("2")
                CG.store_reg(er_result, "$t0", "$t1", "$t2")
            else:
                raise SemanticError("Operator %s incompatible with type BOOL"
                                    % operator,
                                    CG.source_file_reader.get_line_data())

        elif    er_lhs.data_type == DataTypes.INT or \
                er_lhs.data_type == DataTypes.CHAR:
            # We can handle comparisons between chars the same way as ints

            # put lhs in t0 and rhs in t1
            CG.load_reg(reg_dest="$t0", er_src=er_lhs, reg_temp="$t2")
            CG.load_reg(reg_dest="$t1", er_src=er_rhs, reg_temp="$t2")

            if operator == "==":
                CG.code_gen("bne", "$t0", "$t1", "1f")
            elif operator == "!=":
                CG.code_gen("beq", "$t0", "$t1", "1f")
            elif operator == "<=":
                CG.code_gen("sub", "$t0", "$t0", "$t1", comment="t0=t0-t1")
                CG.code_gen("bgtz", "$t0", "1f")
            elif operator == "<":
                CG.code_gen("sub", "$t0", "$t0", "$t1", comment="t0=t0-t1")
                CG.code_gen("bgez", "$t0", "1f")
            elif operator == ">=":
                CG.code_gen("sub", "$t0", "$t1", "$t0", comment="t0=t1-t0")
                CG.code_gen("bgtz", "$t0", "1f")
            elif operator == ">":
                CG.code_gen("sub", "$t0", "$t1", "$t0", comment="t0=t1-t0")
                CG.code_gen("bgez", "$t0", "1f")
            else:
                raise SemanticError("Operator %s incompatible with type %r"
                                    % (operator, er_lhs.data_type),
                                    CG.source_file_reader.get_line_data())
            CG.code_gen("li", "$t0", 1, comment="Test was true")
            CG.code_gen("b", "2f")
            CG.code_gen_label("1", comment="Failed test")
            CG.code_gen("li", "$t0", 0, comment="Test was false")
            CG.code_gen_label("2", comment="After test result saved to t0")
            er_result.data_type=DataTypes.BOOL       # boolean 1=T, 0=F
            CG.store_reg(er_result, "$t0", "$t1", "$t2")


        elif er_lhs.data_type == DataTypes.FLOAT:
            branch_inst = "bc1f"
            # put lhs in f0 and rhs in f1
            CG.load_reg(reg_dest="$f0", er_src=er_lhs, reg_temp="$t0",
                        use_coprocessor_1=True)
            CG.load_reg(reg_dest="$f1", er_src=er_rhs, reg_temp="$t0",
                        use_coprocessor_1=True)
            if operator == "==":
                CG.code_gen("c.eq.s", "$f0", "$f1",
                            comment="Check if equal")
            elif operator == "!=":
                CG.code_gen("c.eq.s", "$f0", "$f1",
                            comment="Check if not equal")
                # negate result
                branch_inst = "bc1t"
            elif operator == "<=":
                CG.code_gen("c.le.s", "$f0", "$f1")
            elif operator == "<":
                CG.code_gen("c.lt.s", "$f0", "$f1")
            elif operator == ">=":
                CG.code_gen("c.le.s", "$f1", "$f0")
            elif operator == ">":
                CG.code_gen("c.lt.s", "$f1", "$f0")
            else:
                raise SemanticError("Operator %s incompatible with type FLOAT"
                                    % operator,
                                    CG.source_file_reader.get_line_data())
            CG.code_gen(branch_inst, "1f")
            CG.code_gen("li", "$t0", 1, comment="Test was true")
            CG.code_gen("b", "2f")
            CG.code_gen_label("1", comment="Failed test")
            CG.code_gen("li", "$t0", 0, comment="Test was false")
            CG.code_gen_label("2")
            er_result.data_type = DataTypes.BOOL       # boolean 1=T, 0=F
            CG.store_reg(er_result, "$t0", "$t1", "$t2")

        else:
            raise SemanticError("Cannot make comparison between types %r and "
                                "%r" % (er_lhs.data_type, er_rhs.data_type),
                                CG.source_file_reader.get_line_data())

        return er_result



    @staticmethod
    def code_gen(instruction, rd=None, rt=None, rs=None, has_label=False,
                 comment=None):
        """
        Generates a line of code, and inserts it into the code file.
        Attempts some basic peephole code optimization.

        Almost all code generation is piped through this function, with a few
        exceptions: gen_labelled_data(), write_prolog(), write_epilogue().
        This was done to facilitate future code optimization.
        :param instruction: The MIPS instruction to use
        :param rd:      The destination register
        :param rt:      The temp register (optional)
        :param rs:      The source register (optional)
        :param comment: Any comment to be added on this line of code
        :return:        None
        """

        # Peephole code optimization: size is one instruction
        if CG.last_instruction:
            if CG.last_instruction["rd"] == rd and \
                    CG.last_instruction["rt"] == rt and (
                        (CG.last_instruction["inst"] == "sw" and
                         instruction == "lw") or
                        (CG.last_instruction["inst"] == "swc1" and
                         instruction == "lwc1")):
                # we are attempting to load the same word we just stored in
                # the last instruction, and it's already in the right register,
                # so we can eliminate this instruction.
                return

        CG.last_instruction = {
            "inst": instruction,
            "rd": rd,
            "rt": rt,
            "rs": rs,
            "has_label": has_label,
            "comment": comment
        }

        f_comment = ""          # Formatted comment
        if comment is not None:
            f_comment = "# " + comment

        start = "\t%s" % instruction
        if has_label:
            # instruction is a label, and it shouldn't be indented
            start = "%s:" % instruction
        elif instruction is None:       # it's just a comment
            start = "\t"

        if rd is None:
            line_of_code = "%s\t\t\t%s" % (start, f_comment)
        elif rt is None:
            line_of_code = "%s\t%s\t%s" % (start, rd, f_comment)
        elif rs is None:
            line_of_code = "%s\t%s,%s\t%s" % (start, rd, rt, f_comment)
        else:
            line_of_code = "%s\t%s,%s,%s\t%s" % \
                           (start, rd, rt, rs, f_comment)
        CG.output(line_of_code)



    @staticmethod
    def code_gen_label(label, comment=None):
        """
        Prints a label, with a comment if available
        :param label:       The label to print
        :param comment:     The comment to print. Optional
        """
        CG.code_gen(label, comment=comment, has_label=True)



    @staticmethod
    def code_gen_comment(comment):
        """
        Prints a comment on its own line of code.
        :param comment:     The comment to print
        """
        CG.code_gen(None, comment=comment)



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
    def push_param(source_exp_rec):
        """
        Pushes a reference to a variable on the stack
        :param source_exp_rec:   ExpressionRecord for the variable to push
        """
        var = ExpressionRecord(data_type=source_exp_rec.data_type,
                               loc=CG.next_offset, is_temp=False,
                               is_reference=True)
        CG.next_offset -= 4

        # if source is a reference, just copy the reference
        if source_exp_rec.is_ref:
            CG.code_gen("lw", "$t0", "%d($fp)" % source_exp_rec.loc,
                        comment="Copy existing pointer")
        # otherwise, make a pointer to the data
        else:
            CG.code_gen("addi", "$t0", "$fp", "%d" % source_exp_rec.loc,
                        comment="Make pointer")
        # put it on the stack
        CG.code_gen("sw", "$t0", "%d($fp)" % var.loc,
                    comment="Add param to stack for param at %d($fp)" % var.loc)



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
            # Trim quotes off of character's lexeme
            value = value[1:-1]
            # map escape characters in lexeme
            mapping = {
                "\\n": '\n',
                "\\t": '\t',
                "\\r": '\r',
                "\\\\": '\\'
            }
            if value in mapping.keys():
                value = mapping[value]
            CG.code_gen("li", "$t0", ord(value))
            CG.code_gen("sw", "$t0", "%d($fp)" % literal.loc)
        elif data_type == DataTypes.FLOAT:
            # make a label
            label, unused_label = CG.gen_label("float")
            # put value into code, at that label
            CG.gen_labelled_data(label, data_type, value)
            CG.code_gen("la", "$t0", label)     # load address of float
            CG.code_gen("lw", "$t0", "($t0)")   # store float in $t0
            # store float on stack
            CG.code_gen("sw", "$t0", "%d($fp)" % literal.loc)
        elif data_type == DataTypes.STRING:
            label, unused_label = CG.gen_label("string")
            CG.gen_labelled_data(label, data_type, value)
            CG.code_gen("la", "$t0", label)
            # store pointer to string on the stack
            CG.code_gen("sw", "$t0", "%d($fp)" % literal.loc)
        return literal



    @staticmethod
    def code_gen_assign(er_dest, er_source, src_subscript=None,
                        dest_subscript=None, is_cast=False):
        """
        Generates code that implements the assignment of er_source to
        er_dest. Can handle references and array subscripts on both sides.
        :param er_dest:         ExpressionRecord for the destination, lhs
        :param er_source:       ExpressionRecord for the source, rhs
        :param src_subscript:   ExpressionRecord for the source subscript
        :param dest_subscript:  ExpressionRecord for the dest subscript
        :param is_cast:         boolean, defines whether or not a cast is
                                occurring
        :return:                None
        """
        assert(isinstance(er_dest, ExpressionRecord) and
               isinstance(er_source, ExpressionRecord))

        dest_type = er_dest.data_type
        source_type = er_source.data_type

        # Verify that lhs and rhs types agree:
        if src_subscript and isinstance(src_subscript, ExpressionRecord):
            source_type = DataTypes.array_to_basic(source_type)
        if dest_subscript and isinstance(dest_subscript, ExpressionRecord):
            dest_type = DataTypes.array_to_basic(dest_type)

        if not is_cast and dest_type != source_type:
            raise SemanticError("Left hand side is not the same type as "
                                "the right hand side.",
                                CG.source_file_reader.get_line_data())

        CG.store_er(er_dest=er_dest, er_src=er_source,
                    src_subscript=src_subscript, dest_subscript=dest_subscript)



    @staticmethod
    def code_gen_if(er_condition, lbl_on_failed_test):
        """
        Generates code that tests if a condition is true, and if the test
        fails, branches to the fail state label.
        :param er_condition:        ExpressionRecord for the test condition
        :param lbl_on_failed_test:  the fail state label
        :return:                    None
        """
        # put er_condition in t0
        CG.load_reg(reg_dest="$t0", er_src=er_condition, reg_temp="$t2")

        CG.code_gen("beq", "$t0", "$0", lbl_on_failed_test)



    @staticmethod
    def make_pointer_to_element_in_array(er_array, er_subscript,
                                         reg_dest, reg_temp):
        """
        Makes a pointer to a value at array[subscript], and puts it in the
        destination register
        :param er_array:        The ExpressionRecord for an array
        :param er_subscript:    The subscript into that array,
                                as an ExpressionRecord
        :param reg_dest:        The destination register
        :param reg_temp:        The temp register
        :return:                A temporary ExpressionRecord, holds value at
                                er_array[er_subscript]
        """
        assert(isinstance(er_array, ExpressionRecord) and
               isinstance(er_subscript, ExpressionRecord))

        # Put subscript into temp register
        CG.load_reg(reg_temp, er_subscript, reg_dest)
        # CG.code_gen("lw", reg_temp, "%d($fp)" % er_subscript.loc,
        #             comment="put subscript in "+reg_temp)
        CG.code_gen("sll", reg_temp, reg_temp, 2,
                    comment="multiply subscript by 4")

        # make a pointer to the array, store it in destination register
        if er_array.is_ref:
            # load pointer to array into reg_dest
            CG.code_gen("lw", reg_dest, "%d($fp)" % er_array.loc,
                        comment="load pointer to array into " + reg_dest)
        else:
            # array is on the stack; it starts at fp + er_array.loc
            CG.code_gen("addi", reg_dest, "$fp", er_array.loc,
                        comment="make pointer to array in " + reg_dest)

        # reg_dest will be a pointer to the value at array[subscript]
        # reg_dest = location of array - subscript*4
        CG.code_gen("sub", reg_dest, reg_dest, reg_temp,
                    comment=reg_dest+" points to value at array[subscript]")



    @staticmethod
    def gen_print(datatype, param_list):
        """
        Generates inline code that calls the syscalls necessary to print
        every ExpressionRecord in the parameter list
        :param datatype:    Not used. Necessary for the other built-in
                            functions, but this one can get the necessary
                            datatype info from param_list
        :param param_list:  the list of ExpressionRecords that holds the
                            values we want to print.
        """
        for er_param in param_list:
            assert(isinstance(er_param, ExpressionRecord))
            if er_param.data_type == DataTypes.INT:
                CG.code_gen_comment("print(int)")
                CG.load_reg("$a0", er_param, reg_temp="$t1", src_subscript=None)
                CG.code_gen("li", "$v0", 1, comment="Syscall for print_int")
                CG.code_gen("syscall")
            elif er_param.data_type == DataTypes.FLOAT:
                CG.code_gen_comment("print(float)")
                CG.load_reg(reg_dest="$f12", er_src=er_param, reg_temp="$t1",
                            src_subscript=None, use_coprocessor_1=True)
                CG.code_gen("li", "$v0", 2, comment="Syscall for print_float")
                CG.code_gen("syscall")
            elif er_param.data_type == DataTypes.CHAR:
                CG.code_gen_comment("print(char)")
                CG.load_reg("$a0", er_param, reg_temp="$t1", src_subscript=None)
                CG.code_gen("li", "$v0", 11, comment="Syscall for print_char")
                CG.code_gen("syscall")
            elif er_param.data_type == DataTypes.STRING:
                CG.code_gen_comment("print(string)")
                CG.load_reg("$a0", er_param, reg_temp="$t1", src_subscript=None)
                CG.code_gen("li", "$v0", 4, comment="Syscall for print_string")
                CG.code_gen("syscall")
            else:
                raise SemanticError("Unsupported argument for print()",
                                    CG.source_file_reader.get_line_data())



    @staticmethod
    def gen_read(datatype, param_list):
        """
        Generates code that calls the read_int, read_float, or read_char
        syscalls.
        :param datatype:    The datatype of the variable to be read
        :param param_list:  Not used. Required for other built-in functions.
        :return:            An ExpressionRecord that holds the result.
        """
        # Make a temp ExpressionRecord to hold the result
        exp_rec = CG.create_temp(datatype)

        if datatype == DataTypes.INT:
            CG.code_gen("li", "$v0", 5, comment="Syscall for read_int")
            CG.code_gen("syscall")
            CG.code_gen("sw", "$v0", "%d($fp)" % exp_rec.loc)
        elif datatype == DataTypes.FLOAT:
            CG.code_gen("li", "$v0", 6, comment="Syscall for read_float")
            CG.code_gen("syscall")
            CG.code_gen("swc1", "$f0", "%d($fp)" % exp_rec.loc)
        elif datatype == DataTypes.CHAR:
            CG.code_gen("li", "$v0", 12, comment="Syscall for read_char")
            CG.code_gen("syscall")
            CG.code_gen("sw", "$v0", "%d($fp)" % exp_rec.loc)
        return exp_rec



    @staticmethod
    def store_er(er_dest, er_src, dest_subscript=None, src_subscript=None):
        """
        Stores the contents of er_src in er_dest.
        If either er_dest or er_src are references, it dereferences them
        before making the assignment.
        If either er_dest or er_src are arrays, it uses the appropriate
        subscripts to figure out where the value should be loaded from or
        assigned.
        :param er_dest:         The destination ExpressionRecord
        :param er_src:          The source ExpressionRecord
        :param dest_subscript:  The destination subscript ExpressionRecord
        :param src_subscript:   The source subscript ExpressionRecord
        :return:                None
        """
        assert isinstance(er_src, ExpressionRecord) and \
               isinstance(er_dest, ExpressionRecord)
        reg_value_to_store = "$t0"
        reg_temp = "$t1"
        reg_temp2 = "$t2"

        # Load whatever is in er_src into reg_value_to_store
        CG.load_reg(reg_dest=reg_value_to_store, er_src=er_src,
                    reg_temp=reg_temp, src_subscript=src_subscript)

        # Store whatever is in reg_value_to_store in er_dest
        CG.store_reg(er_dest, reg_src=reg_value_to_store, reg_temp=reg_temp,
                     reg_temp2=reg_temp2, dest_subscript=dest_subscript)



    @staticmethod
    def load_reg(reg_dest, er_src, reg_temp, src_subscript=None,
                 use_coprocessor_1=False):
        """
        Loads whatever value that a source ExpressionRecord points to into a
        register
        :param reg_dest:        The register that will hold the desired value
        :param er_src:          The ExpressionRecord that points to the value
        :param src_subscript:   Subscript into er_src, if er_src is an array.
                                Must be an ExpressionRecord.
        :param use_coprocessor_1:   If the value needs to be loaded into a
                                    floating point register, this will cause
                                    the 'lwc1' instruction to be used instead of
                                    'lw'.
        :return:                None
        """
        assert isinstance(er_src, ExpressionRecord)

        instruction = "lw"
        if use_coprocessor_1:
            instruction = "lwc1"

        if er_src.is_array():
            assert isinstance(src_subscript, ExpressionRecord)
            # put ptr to source data in reg_value_to_store
            CG.make_pointer_to_element_in_array(er_src, src_subscript,
                                                reg_dest, reg_temp)
            # dereference ptr to source data; put it in reg_value_to_store
            CG.code_gen(instruction, reg_dest, "(%s)" % reg_dest)
        elif er_src.is_ref:
            # put ptr to source data in reg_temp
            CG.code_gen("lw", reg_temp, "%d($fp)" % er_src.loc)
            # dereference ptr to source data; put it in reg_value_to_store
            CG.code_gen(instruction, reg_dest, "(%s)" % reg_temp)
        else:
            # put source data in reg_value_to_store
            CG.code_gen(instruction, reg_dest, "%d($fp)" % er_src.loc)



    @staticmethod
    def store_reg(er_dest, reg_src, reg_temp, reg_temp2, dest_subscript=None,
                  use_coprocessor_1=False):
        """
        Copies the value in a source register to er_dest. If er_dest is a
        reference, it dereferences it before making the assignment. If
        er_dest is an array, it uses the destination subscript to figure out
        where the value should be assigned.
        :param er_dest:         The destination ExpressionRecord
        :param reg_src:         The source register
        :param reg_temp:        A temporary register
        :param reg_temp2:       A different temp register
        :param dest_subscript:  The destination subscript ExpressionRecord
        :param use_coprocessor_1:   Set this to true if you need to store
                                    floating point numbers in coprocessor 1.
        :return:                None
        """
        assert isinstance(er_dest, ExpressionRecord)

        store_inst = "sw"
        if use_coprocessor_1:
            store_inst = "swc1"

        if er_dest.is_array():
            assert isinstance(dest_subscript, ExpressionRecord)

            # put ptr to destination in reg_temp
            CG.make_pointer_to_element_in_array(er_dest, dest_subscript,
                                                reg_temp, reg_temp2)
            # store source data in destination
            CG.code_gen(store_inst, reg_src, "(%s)" % reg_temp,
                        comment="Store data at array[subscript]")
        elif er_dest.is_ref:
            # put ptr to destination in reg_temp
            CG.code_gen("lw", reg_temp, "%d($fp)" % er_dest.loc)
            # store source data in destination
            CG.code_gen(store_inst, reg_src, "(%s)" % reg_temp,
                        comment="Store data by reference")
        else:
            CG.code_gen(store_inst, reg_src, "%d($fp)" % er_dest.loc,
                        comment="Store directly on the stack")



    @staticmethod
    def gen_cast(destination_type, param_list):
        """
        Generates code that changes the datatype of a parameter.
        Supports changing CHAR -> INT, INT -> FLOAT, FLOAT -> INT
        :return:    An ExpressionRecord where the parameter ExpressionRecord
                    has changed to destination_type
        """
        if len(param_list) != 1:
            raise SemanticError("Casting functions require one argument",
                                CG.source_file_reader.get_line_data())
        er_input = param_list[0]
        assert(isinstance(er_input, ExpressionRecord))
        assert(isinstance(destination_type, DataTypes))
        if er_input.data_type == destination_type:
            return er_input
        er_output = CG.create_temp(destination_type)

        if er_input.data_type == DataTypes.CHAR and \
                destination_type == DataTypes.INT:
            CG.code_gen_assign(er_dest=er_output, er_source=er_input,
                               is_cast=True)
        elif er_input.data_type == DataTypes.INT and \
                destination_type == DataTypes.FLOAT:
            # Convert int to float
            CG.load_reg("$f0", er_input, reg_temp="$t1", use_coprocessor_1=True)
            CG.code_gen("cvt.s.w", "$f0", "$f0")
            CG.store_reg(er_output, "$f0", reg_temp="$t1", reg_temp2="$t2",
                         use_coprocessor_1=True)
        elif er_input.data_type == DataTypes.FLOAT and \
                destination_type == DataTypes.INT:
            # Convert float to int
            CG.load_reg("$f0", er_input, reg_temp="$t1", use_coprocessor_1=True)
            CG.code_gen("cvt.w.s", "$f0", "$f0")
            CG.store_reg(er_output, "$f0", reg_temp="$t1", reg_temp2="$t2",
                         use_coprocessor_1=True)
        else:
            raise SemanticError(
                "Unsupported operation: cast value of type %r to %r." %
                (er_input.data_type, destination_type),
                CG.source_file_reader.get_line_data())
        return er_output



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
        assert isinstance(func_rec, FunctionSignature) and \
            isinstance(func_rec.label, str)

        # store parameters and returned value
        # TODO: should not declare a new variable, just make space on stack
        er_retval = CG.declare_variable(func_rec.return_type, "return_var",
                                        size=1)

        for er_param in params:
            # push param val on stack
            CG.push_param(er_param)

        # In new function, return var is at (4*len(params)+8)($fp),
        # params are at 4($fp) thru (4*len(params)+4)($fp)


        # We know that the sp should be at CG.next_offset from fp
        CG.code_gen("addi", "$sp", "$fp", CG.next_offset)

        # store control link and return address
        CG.code_gen("sw", "$fp", "($sp)", comment="store old control link")

        CG.code_gen("move", "$fp", "$sp", comment="make new control link")
        CG.code_gen("addi", "$sp", "$sp", -4)
        CG.code_gen("sw", "$ra", "($sp)", comment="store return address")

        # call the function
        CG.code_gen("jal", func_rec.label)

        # restore control link and return address
        CG.code_gen("lw", "$ra", "-4($fp)", comment="restore old ra")
        CG.code_gen("move", "$sp", "$fp", comment="restore old sp")
        CG.code_gen("addi", "$sp", "$sp", 4*(len(params)+1),
                    comment="remove params and control link from stack")
        CG.code_gen("lw", "$fp", "($fp)", comment="restore old fp")

        return er_retval


