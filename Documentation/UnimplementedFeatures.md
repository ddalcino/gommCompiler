
## Unimplemented features, planned for future release:


#### Code Optimization.

Currently, very little has been done in terms of code optimization. Peephole
optimization has been implemented, using a window of two instructions.
Register allocation should be implemented in the next release, with
strength reduction planned for the following release.


#### Boolean Datatype

One strange and unsatisfying thing about the language in its current state
is that it does not handle Boolean variables. Booleans are already used
internally by the compiler, and it should be fairly simple to implement
them fully for users. Full support is planned for the next release.


#### String Datatype

Currently, strings are immutable, and may only occur in user code as
literals. They cannot be assigned to variables yet, but the next release
should have support for variables that point to dynamically-allocated,
modifiable strings.


#### Built-in File-Handling

Built-in functions that open, read, write, seek, and close files are planned
for the next release.


#### Size-Aware Arrays

Currently, arrays can only be statically declared at compile time. It would
be very simple to keep track of the size of the array, and check the
subscript against that size at runtime. This feature is planned for the
next release. Currently, there are no checks on the subscript values at
all; not even a check for negative numbers. This makes it very easy for
user code to read and overwrite any value on the stack.


#### Range-Based For Loops

The addition of size-aware arrays makes it easy to automatically generate
for loops that safely traverse an array. Range-based for loops are safer,
and much easier to write, than a while loop that traverses the same array.
This is the proposed syntax for range-based for loops, planned for the next
release:

	for (reference_id datatype in array_id) {
		# use reference_id to access an element in the array
	}


#### Function Prototype Flexibility

Function prototypes currently require that the identifiers for each
parameter and return value are specified in the prototype, where they are
unnecessary. This is unacceptable for the next release. The next release
should either make the identifiers optional, or do away with the necessity
for prototypes altogether by adding a second pass to the compiler that
finds all function signatures on its own, before defining the functions.


#### User-Defined Datatypes

The addition of structures will make user code much more capable, and will
make it significantly easier to write a Go-- compiler in the Go-- language.
This is not planned for the next release, but it will be coming eventually.

