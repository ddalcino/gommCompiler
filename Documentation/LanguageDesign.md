# Go-- Language Design

This file documents a project for a graduate-level compiler design class. 
The project entails the design of a programming language and the 
implementation of a compiler that translates code written in that language
to MIPS assembly code. My language is called 'Go--', since it is partially 
based on the Go programming language. The '--' is to denote that it has 
fewer features than Go. The name is a misnomer; this language has far more
in common with C than it does Go.

#### Datatypes

Datatypes include integers (int), floats (float), and characters (char).
Variables can only be declared as being one of these three datatypes, or as
an array of these datatypes.

Strings also exist, but they cannot be assigned to variables (that feature
has been postponed to the next version of Go--); they may only exist as
literals, and the only thing you can do with them is print them to the
screen. Users are welcome to use char arrays as strings, and write their
own char array handling routines, but native support for that kind of
string has been omitted.

Booleans exist in the language, but they cannot be assigned to variables
(that feature has been postponed to the next version of Go--). The only way
to generate a boolean value is to use a relational operator between two
expressions. The operators \<, \<=, >, >=, ==, and != can be used between two
expressions of type int, float, or char as long as the datatypes agree with
each other, and the result will be a boolean value. The operators && and ||
can only be used between two boolean values, and return another boolean
value. These values are only useful in if and while statements.

Variables must be declared before being used. A declaration statement is in
the form:

    'var' <identifier> <datatype>.

Arrays of any of the three datatypes may be declared, using a declaration
statement in the form:
 
    'var'<identifier> [<size>]<datatype>. 

The `<size>` parameter must be an integer literal, because it must be available at
compile time. Array size is set at compile time and may not change during
runtime.

#### Functions

Subroutines are functions that return a single value of a single type (not
an array, and not void). Parameters are always passed by reference. A
function may be declared in the form:

    'func' <identifier> '(' [<param identifier> <param type>{, <param identifier> <param type>}] ')'
        <return identifier> <return datatype> '{' <function body> '}'

Subroutines must either be defined or forward declared before they are used.
This makes it possible to write a compiler that runs in a single pass, and
allows a programmer to use different kinds of recursion. An example of this
is found in the calculator sample program, which implements a rudimentary
form of recursive descent. 

A forward declaration statement is in the form:

    'proto' <identifier> '(' [<param identifier> <param type>{, <param identifier> <param type>}] ')' 
        <return identifier> <return datatype> ';' 

There is no good reason to require the parameter and return identifiers in the
forward declaration, but it makes the compiler easier to write; support for
omitting these identifiers is planned for the next release.

Code is case-sensitive. Whitespace is ignored. Comments may exist on any
line, but they must be preceded by a `#` character; the `#` character denotes
that everything to the right of it is a comment.


---
## Lexical elements:

### Identifiers:

Identifiers must begin with a letter a-z or A-Z or an underscore (\_)
character. After the first character, they may include any letter a-z, A-Z,
\_, or any number 0-9. All identifiers are case-sensitive.

This language requires the declaration of return variables; however, not
every function will use these variables. In the case where a variable will
not be used, it is considered good style to give it the identifier '\_';
this implies that it will not be used. Nothing will stop a programmer from
using a variable named '\_', although that programmer's code will look a
little odd.


### Literals

##### Numeric literals:

    <numeric_literal> ::=
        <integer_literal>  | <float_literal>

##### Integer literals
    <integer_literal> ::=
        (0|1|2|3|4|5|6|7|8|9|0)+

##### Floating point literals
    <float_literal> ::=
        (0|1|2|3|4|5|6|7|8|9|0)+(.)(0|1|2|3|4|5|6|7|8|9|0)+

##### Character literals: 
A single character, a-z or A-Z or 0-9, surrounded by
single quotes. Escape characters for newline (\n), tab (\t), carriage
return (\r), and backslash (\\) are also supported. These are the only
characters that the language design requires a compiler to support, but it
does not restrict a compiler from supporting others.

    <char_literal> ::=
        '<char_contents>'
    <char_contents> ::=
        (a-zA-Z0-9) | \n | \r | \t | \\
    <string_literal> ::=
        "<string_contents>"
    <string_contents> ::=
        {<char_contents>}

### Comments:

Comments may exist on any line, but they must be preceded by a `#` character;
the `#` character denotes that everything to the right of it is a comment, up
until the newline character.

    <comment> ::=
        #<anything_except_newline>\n

### Reserved words: 
These words cannot be used as identifiers.

	var    float  if   while  func
	int    char  else  return  proto



---
## Declarations and Types:

    <declaration_statement> ::=
        <variable_declaration>  |  <array_declaration>
    
    <variable_declaration> ::=
        var <identifier> <datatype>

### Array declaration:

Arrays of any of the three datatypes may be declared. The array size
parameter must be available at compile time, because array size is set at
compile time and may not change during runtime. Currently, the only way to
do this is with an integer literal.

    <array_declaration> ::=
        var <identifier> [<array_size>]<datatype>
    
    <array_size> ::=
        <integer_literal>

### Datatypes:

    <datatype> ::=
        int  | float  | char


### Function declaration:

Functions are subroutines that return a single value of a single type (not
an array, and not void). The return value is stored in a variable
identified in the function declaration, so that when it comes time to
return from the function, it is necessary to type `return`, but not the
value to return, and not the identifier of the return value, because doing
so would be redundant (and a compilation error).

Parameters are always passed by reference.

Functions may be forward declared as prototypes, so that they can be used
before they are defined.

    <function_prototype> ::=
        proto <identifier> (<param_list>) <return identifier> <return datatype> ';'

    <function_definition> ::=
        func <identifier> (<param_list>) <return_identifier> <return_datatype>
        '{'<code_block>'}'

    <param_list> ::=
        [<basic_declaration>{, <basic_declaration> }]

    <return_identifier> ::=
        <identifier>

    <return_datatype> ::=
        <datatype>

    <code_block> ::=
        <statement> <code_block> | <statement>



---
## Expressions:

### Arithmetic Expressions:

Arithmetic expressions are only supported when all operands are of the same
datatype; either int or float. Arithmetic expressions are evaluated in this
order: Parentheses, followed by Multiplication/Division/Modulus, followed by
Addition/Subtraction.

    <arithmetic_expression> ::=
        <term> {+- <term>}

    <term> ::=
        <relfactor> {*/ <relfactor>}

    <relfactor> ::=
        <factor> <relop> <factor>

    <relop> ::=
        == | != | < | <= | >= | >

    <factor> ::=
        variable_identifier>  |
        <numeric_literal>  |
        <array_identifier>'['<arithmetic_expression>']'  |
        '(' <arithmetic_expression> ')'


---
## Statements:

    <statement> ::=
        <assignment_statement> | <if_statement>         | <while_statement>  |
        <return_statement>     | <declaration_statement>


#### Assignment Statements:

Assignment statements are only supported when the datatype of the right hand side agrees 
with the datatype of the left hand side.

    <assignment_statement> ::=
        <variable_identifier> = <arithmetic_expression> ';'


#### If Statements:

    <if_statement> ::=
        if (<arithmetic_expression>) '{' <code_block> '}' [else '{' <code_block> '}']

#### Loop Statements:

    <loop_statement> ::=
        while (<arithmetic_expression>) '{' <code_block> '}'


#### Return Statements:

Return values are stored in the return variable, identified at the top of
the function declaration. It is unnecessary to identify the return variable
or value in the return statement.

    <return_statement> ::=
        return ';'


---
## Built-in IO functions


### Output:

The language has a built-in print function that can print a comma separated
list of values, which can be arithmetic expressions, variables, or
literals, as long as they evaluate to a single integer, float, char, or
string value.

    func print({param})


### Keyboard Input:

The language has built-in keyboard input functions that read floats, ints,
or chars.

    func read_int() int
    func read_float() float
    func read_char() char



### Casting

The language also has built-in casting functions that can turn values into
int or float values. A more capable set of casting functions is planned for
the next version.

    func cast_int(char) int
    func cast_int(float) int
    func cast_float(int) float


---
## Complete grammar summary:

    <program> ==>
        1 {<func_decl_or_proto>}
  
    <func_decl_or_proto> ==>
        2 <function_decl> |
        3 <function_prototype>

    <function_prototype> ==>
        4 TokenType.KeywordProto TokenType.Identifier TokenType.OpenParen <param_list> 
            TokenType.CloseParen <return_identifier> <return_datatype> TokenType.Semicolon

    <function_decl> ==>
        5 TokenType.KeywordFunc TokenType.Identifier TokenType.OpenParen <param_list> 
            TokenType.CloseParen <return_identifier> <return_datatype> TokenType.OpenCurly 
            <statement_list> TokenType.CloseCurly

    <param_list> ==>
        6 [TokenType.Identifier <datatype> {TokenType.Comma TokenType.Identifier <datatype>} ]

    <datatype> ==>
        8 TokenType.KeywordInt |
        9 TokenType.KeywordFloat |
        10 TokenType.KeywordChar |
        11 TokenType.OpenBracket TokenType.Integer TokenType.CloseBracket |
        <array_of_datatype>

    <array_of_datatype> ==>
        12 TokenType.KeywordInt |
        13 TokenType.KeywordFloat |
        14 TokenType.KeywordChar
  
    <return_identifier> ==>
        15 TokenType.Identifier
  
    <return_datatype> ==>
        16 <datatype>
  
    <statement_list> ==>
        17 {<basic_statement>}

    <basic_statement> ==>
        19 <return_statement> |
        20 <if_statement> |
        21 <while_statement> |
        22 <declaration_statement> |
        23 <assignment_or_function_call>

    <assignment_or_function_call> ==>
        24 TokenType.Identifier TokenType.AssignmentOperator <expression> TokenType.Semicolon |
        25 TokenType.Identifier TokenType.OpenBracket <expression> TokenType.CloseBracket 
            TokenType.AssignmentOperator <expression> TokenType.Semicolon |
        26 TokenType.Identifier TokenType.OpenParen <expression_list> TokenType.CloseParen 
            TokenType.Semicolon

    <expression_list> ==>
        27 [<expression> {, <expression>}]

    <code_block> ==>
        29 TokenType.OpenCurly <statement_list> TokenType.CloseCurly

    <return_statement> ==>
        30 TokenType.KeywordReturn TokenType.Semicolon

    <if_statement> ==>
        31 TokenType.KeywordIf TokenType.OpenParen <expression> TokenType.CloseParen 
            <code_block> [ TokenType.KeywordElse <code_block> ]

    <declaration_statement> ==>
        33 TokenType.KeywordVar TokenType.Identifier <datatype> TokenType.Semicolon

    <while_statement> ==>
        34 TokenType.KeywordWhile TokenType.OpenParen <expression> TokenType.CloseParen <code_block>

    <expression> ==>
        35 <term> { TokenType.AddSubOperator <term> }

    <term> ==>
        39 <relfactor> { TokenType.MulDivModOperator <relfactor> }

    <relfactor> ==>
        40 <factor> [TokenType.RelationalOperator <factor>]

    <factor> ==>
        44 TokenType.OpenParen <expression> TokenType.CloseParen |
        45 <variable_or_function_call> |
        46 <literal>

    <variable_or_function_call> ==>
        49 TokenType.Identifier TokenType.OpenBracket <expression> TokenType.CloseBracket |
        50 TokenType.Identifier TokenType.OpenParen <expression_list> TokenType.CloseParen |
        51 TokenType.Identifier

    <literal> ==>
        57 TokenType.Float |
        58 TokenType.Integer |
        59 TokenType.Char |
        60 TokenType.String

