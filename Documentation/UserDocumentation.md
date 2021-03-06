
## User Documentation

The Gomm Compiler requires Python3 to run. First install Python3 (available
at Python.org) if you haven't already. It has been tested primarily using
Python 3.5.1, so install that version or above if possible. Copy the
contents of the GommCompiler folder to your desired working directory, and
you will be ready to run the compiler.

To compile a Go-- source code file called 'source.gomm', type the following
at the command line:

	$ python3 ./GommCompiler.py ./source.gomm

The `./` is to denote the current working directory. Replace these with the
correct paths to the GommCompiler source and your source file, if
necessary.

To learn how to write Go-- code, refer to the LanguageDesign.txt file for
language documentation, and the sample code files in the sample code
directory. A few helpful hints:

+ Go-- does not support negative literal values at this point. If you need to
  make a negative number, try using '0-n' where n is a positive number.

+ Strings are just literals; you can't assign them to a variable, or alter
  them programmatically.

+ Every function declaration requires the declaration of a return variable. If
  you don't plan to use this variable, it is good style to name it '_'; this
  implies that you aren't going to use it.

+ You don't need to type 'return' at the end of a function; it will be added
  automatically, and the return variable you defined in the function
  declaration will be returned to the caller automatically.


#### Using the compiler:

When you compile a source code file, the compiler will first print the name
of the source file, followed by a string of numbers from 1 to 60. These
numbers correspond to the grammar productions listed in the
LanguageDesign.txt file; these can be useful for determining what the
compiler thought your code meant. After that, it may give some error
messages, but if it does, it will try to continue compilation so it can
tell you what else may be wrong with your code. If any error messages are
reported, compilation will not conclude successfully, and you won't end up
with an assembly output file.


#### Interpreting Error Messages:

In general, error messages will be displayed with a display of the line 
where the error occurred, along with the line and column numbers, and an 
arrow pointing to the location of the error. This arrow is often a little 
bit off. It may point to the right of the error's location, or on the next 
line. It's a good habit to look at the source code directly, and look at 
what happened right before the location the error was reported. Also, it's 
a good idea to start by looking at the first error the compiler reports; 
later errors may not actually be errors, but misinterpretations of correct 
code that were thrown off by the first error.

+ RedeclaredVariableError: This error may occur if you are declaring a 
  variable or function with the same name as another variable or function. 
  Try using a different variable name.

+ UseUndeclaredVariableError: This error may occur if you start using a 
  variable without declaring it. Check your spelling and make sure to 
  declare variables before you use them.

+ MatchError and ProductionNotFoundError: These can occur when syntax is 
  incorrect. Check the syntax specified in the LanguageDesign.txt 
  documentation to ensure that your syntax is correct.  
  One common MatchError occurs when you fail to leave at least one empty 
  line at the end of the program. Make sure to leave a blank line at the end!
  Another common mistake occurs when writing boolean expressions: expressions 
  on either side of the boolean operator must be surrounded by parentheses, 
  unless they consist of a single literal or variable.

+ SemanticError: This usually occurs if an expression's datatype is 
  incorrect or not supported by the operation being done on it. These 
  errors usually include a more descriptive error message regarding what 
  went wrong, so pay attention to what it says.

