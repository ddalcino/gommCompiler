
class CodeGenerator:

    prologue = '\t.text\n' \
               '\t.globl main\n' \
               'main:\n' \
               '\tmove\t$fp $sp\n' \
               '\tla $a0 ProgStart\n' \
               '\tli $v0 4                    # Print Syscall\n' \
               '\tsyscall\n'

    epilogue = '\tla $a0 ProgEnd\n' \
               '\tli $v0 4                    # Print Syscall\n' \
               '\tsyscall\n' \
               '\tli $v0 10                   # Exit Syscall\n' \
               '\tsyscall\n' \
               '\t.data\n' \
               'ProgStart:\t.asciiz\t"Program Start\n"' \
               'ProgEnd:\t.asciiz\t"Program End\n"'

    def __init__(self):
        self.functions = {}
        pass

    def write_prolog(self):
        """
        Writes a prologue to the asm file
        :return:
        """
        pass

    def write_epilogue(self):
        """
        Writes an epilogue to the asm file
        :return:
        """


    def write_function(self, identifier, param_list):
        """

        :return:
        """

        # Use param_list to decide how large to make the stack:
        # Assume that each parameter is 4 bytes
        # Add an extra 8 bytes for the return address and frame pointer
        stack_entry_size = 4 * (len(param_list) + 2)

        # The index of the function
        index = len(self.functions)

        # The name of the function
        function_name = "function_%d" % index
        self.functions[identifier]={
            "asm_name": function_name,
            "param_list": param_list
        }

        # Write the function label and open the stack frame
        function_prologue = \
            '%s:\n' % function_name + \
            '\taddiu\t$sp, $sp, -%d\n' % stack_entry_size + \
            '\tsw\t$ra, %d($sp)\n' % (stack_entry_size-4) +\
            '\tsw\t$fp, %d($sp)\n' % (stack_entry_size-8) +\
            '\taddiu\t$fp, $sp, %d\n' % stack_entry_size

        # Restore return address, frame pointer, stack pointer, and return
        function_epilogue = \
            '\tlw\t$ra, %d($sp)\n' % (stack_entry_size-4) +\
            '\tlw\t$fp, %d($sp)\n' % (stack_entry_size-8) +\
            '\taddiu\t$sp, $sp, %d\n' % stack_entry_size +\
            '\tjr\t$ra\n'






