############################################
PyPE - Python Parsing Expressions (Overview)
############################################

PyPE is a python pattern matching library for searching text and extracting
data from the text. While PyPE can be used to match text patterns in any text
file, it is particularly useful for interpreting structured text and converting 
the text into data structures that can be used in a program. Examples of
text with structure are html or xml documents, comma separated value or tab
delimited files, or source code files. The code used to interpret structured
text and convert it to data structures is referred to as a parser. PyPE is
used to create a specific type of parser called a parsing expression grammar
(PEG).

A parsing expression grammar is used to represent the structure of a text
document in a way that allows the document to be parsed. PEGs are similar in
purpose to regular expressions. PEGs tend to be more verbose than regular
expressions, but when well written are often easier to interpret. PEGs are also
more flexible than regular expressions and can be used to parse complex
recursive grammars such as programming languages. While PEGs are more powerful
than regular expressions, they are also often easier to write.

Parsing expressions use a declarative programming style, where the structure
of a text input is defined and the information to capture is specified without
indicating how the text input will be processed. Once the syntax of the text
input is described, the PEG parser can be passed a string and will return the
data extracted from the string in a data structure that can be used in the
program or can be converted into a form needed within the program.

PyPE is modeled after the Lua LPEG (Lua Parsing Expression Grammars) library.
The syntax has been preserved where possible, although some of the operators
in Python use a different syntax than Lua and not all of the operations of LPEG
are included, and some additional features that are not part of LPEG are added.
For example, support for debugging a grammar is built into PyPE.

PyPE also includes a :class:`Tokenizer` class that is used to create a tokenizing
parser, where each token is defined using a PyPE pattern. The :class:`Template`
engine class is also included with PyPE. A template engine is code that processes
a template document with embedded scripting (in this case python scripting) and
produces a document with dynmamic content from the embedded scripting logic.

The PyPE repository can be found at: https://bitbucket.org/llarsen/pype/

====================
PyPE Library Summary
====================

The PyPE library can be divided into a few major categories:

* :ref:`pattern-ops` - These are used to specify patterns to use for matching
  text.

* :ref:`predefined-patterns` - A few commonly used predefined patterns are
  made available in the library.

* :ref:`capture-ops` - These are used to specify information should be
  captured and returned when matching a text using a PEG.

* :ref:`place-holder` - A place holder is needed when a pattern needs to be
  included that has not been defined yet. This occurs for recursive patterns.
  Once the neceesary pattern(s) have been defined they can be substituted into
  the parsing expression via the ``setVs`` function.

* :ref:`stack-ops` - A stack is just a named array that works similar to the
  capture array. In some cases, it is useful to add captured data to a stack
  that is independent of the capture array.

* :ref:`utility-functions` - Other functions that can be used with PEGs.

To check if a string matches a pattern defined using PyPE, the patterns
``match`` function is called. If the string is a match a ``Match`` object
is called. This is discussed in :ref:`match-object`. A few other classes are
inlcuded in the PyPE package.

* :ref:`Tokenizer` - This class aids in creating tokenizing parsers.

* :ref:`Template` - A template engine class useful for embedding scripting logic
  in text files for dynamic tex file creation.

.. _pattern-ops:

Pattern Operators
=================

The following table summarizes the basic operations for creating patterns for
matching text:

+-------------+----------------------------------------------------------------+
| Operator    | Description                                                    |
+=============+================================================================+
| P(string)   | Matches the specified string exactly.                          |
+-------------+----------------------------------------------------------------+
| P(n)        | Matches exactly n characters.                                  |
+-------------+----------------------------------------------------------------+
| P(-n)       | Matches less than n characters only. For example, P(-1) only   |
|             | matches the end of the string since it only matches if less    |
|             | than one character is left in the string.                      |
+-------------+----------------------------------------------------------------+
| P(bool)     | Always True or always False pattern (based on boolean value).  |
+-------------+----------------------------------------------------------------+
| P(fn)       | For function with signature ``fn(string, idx, context)`` return|
|             | the next index associated with the match. Must be larger than  |
|             | the index that was passed in and less than or equal to the     |
|             | string length. The return value may also be False or None if   |
|             | the pattern fails. It may also be a                            |
|             | :class:`Match <PyPE.PyPE.Match>` object.                       |
+-------------+----------------------------------------------------------------+
| I(string)   | Case insensitive string match.                                 |
+-------------+----------------------------------------------------------------+
| S(string)   | Match any character in the specified string.                   |
+-------------+----------------------------------------------------------------+
| R(range)    | Match any character that comes between the two specified       |
|             | characters in the ASCII table - the character with the lowest  |
|             | ASCII value must be specified first.                           |
+-------------+----------------------------------------------------------------+
| SOL()       | Matches the start of a line.                                   |
+-------------+----------------------------------------------------------------+
| EOL()       | Matches the end of a line.                                     |
+-------------+----------------------------------------------------------------+
| ptn1 * ptn2 | Match ``ptn1`` followed by ``ptn2``. For the pattern to be a   |
|             | match, both ``ptn1`` and ``ptn2`` must be a match.             |
+-------------+----------------------------------------------------------------+
| ptn1 + ptn2 | Match ``ptn1`` or ``ptn2``. The patterns are checked in the    |
|             | order than they appear, so ``ptn2`` is only checked for a match|
|             | if ``ptn1`` fails.                                             |
+-------------+----------------------------------------------------------------+
| ptn1 - ptn2 | Match ``ptn1`` with the exception of ``ptn2``. In other words, |
|             | only match ``ptn1`` only if ``ptn2`` fails.                    |
+-------------+----------------------------------------------------------------+
| -ptn1       | Match anything but ``ptn1``. Consumes no input.                |
+-------------+----------------------------------------------------------------+
| ~ptn1       | Match the ``ptn1``, but consume no input.                      |
+-------------+----------------------------------------------------------------+
| ptn1**n     | Match ``ptn1`` at least n times.                               |
+-------------+----------------------------------------------------------------+
| ptn1**-n    | Match ``ptn1`` at most n times. Always succeeds.               |
+-------------+----------------------------------------------------------------+
| ptn1**[n]   | Match ``ptn1`` exactly n times.                                |
+-------------+----------------------------------------------------------------+
| ptn / fn    | Pass the match object to the given function. Return the result |
|             | from the function, which should be the match object or None.   |
|             | As manipulation of captures, such as type conversion, is a     |
|             | common use for this, this will be convered in the              |
|             | :ref:`capture-ops` section.                                    |
+-------------+----------------------------------------------------------------+

:class:`P(string) <PyPE.PyPE.P>` matches the given string exactly. Once a pattern
has been defined, the pattern's ``match(string, index)`` function can be called 
with a string and a starting index. The ``match`` function will test whether the
string matches the pattern starting at the given index. The index parameter is
optional and has a default value of 0, which is the index for the start of the
string. An index of 1 indicates the second character, 2 the third character, and
so on.

  >>> ptn = P('test')
  >>> match = ptn.match('testing')
  >>> print(match)
  'test'
  >>> ptn.match('testing', 1) == None    # match starting at 'e' fails 
  True

Note that the pattern above only matches the string 'test' once. The following is 
an example of a simple pattern that can be used to check for a digit::

  >>> digit = R('09')  # Read characters in the range 0-9

Again, this pattern matches only a single digit. A string can be checked to see if it
matches the pattern by calling the pattern's match function::

  >>> match = digit.match('56a7')
  >>> print(match)
  '5'

In order to match a pattern multiple times, the `**` operator is used. The following
is used to match one or more digits::

  >>> digits = R('09')**1
  >>> match = digits('56a7')
  >>> print(match)
  '56'

The 'or' operator is represented by the `+` symbol. The following is an example of a 
pattern that finds any one of three different ways of representing a new line in a text 
file::

  >>> newline = P('\r\n') + P('\r') + P('\n')

Note that this is an ordered search, meaning that if ``newline.match(string)`` is
called, the ``newline`` pattern checks if the string starts with the first expression 
``P('\r\n')``, and if this fails to match, the ``newline`` pattern checks if the
string starts with the second pattern ``P('\r')``. If this fails to match, the third 
pattern ``P('\n')`` is tested. If any of the three patterns succeeds, then the pattern
succeeds and the matched characters are returned. However, if all three patterns fail, 
then the patterb fails and ``None`` is returned from the `match` function.

Note that the ordering of the three patterns matters. For example, the following 
pattern will never return the result ``\r\n`` because ``\r`` will always be matched 
first.

  >>> newline = P('\r') + P('\r\n') + P('\n')

Patterns can be combined to make more complex expressions::

  >>> anything_but_newline = P(1)-newline           # Match anything with the exeption of newline
  >>> read_line = anything_but_newline**0 * newline
  >>> print(read_line.match("123\n456"))            # Note newline is included in match
  '123\n'

Sometimes a parsing expression will behave in a way that you did not expect. Typically
this is because there are edge cases that you did not consider when building the expression.
For example consider the ``read_line`` pattern above. Suppose we try and apply this to the
string "456"::

  >>> print(to_end_of_line.match("456"))
  None

The ``read_line`` pattern fails to read this line. The reason that it fails is that this
string does not include a newline at the end. In other words, our ``read_line`` pattern
will read any line from a file except for the last line. This is probably not what was 
intended. The correct pattern to use for reading any line from a file is::

  >>> read_line = anything_but_newline**0 * newline**-1

This ``read_line`` pattern can be read as 'Match zero or more of any character but newline, 
followed by at most one newline'. If there is no newline at the end, the pattern is still 
satisfied. When we try to read the string "456", we now get the expected result::

  >>> print(to_end_of_line.match("456"))
  '456'

Custom Patterns
---------------

There may be cases more complex logic is needed than is provided by the built in 
pattern operations. In this case a custom function can be created that performs
the match. The function has the form ``fn(string, index, context)`` where the
``string`` is the string to which the pattern is applied, the ``index`` is the
current location in the string for testing the pattern that the function matches, 
and the ``context`` is a `Context` object which gives access to capture stacks.
Below is a very simple example of a custom pattern::

  >>> def take2(string, idx, ctxt):
  >>>     return i+2
  >>> ptn = P(take2)
  >>> match = ptn.match("123")
  >>> print(match)
  '12'

This simple pattern just takes 2 character from the string. Note that this is not
a safe implementation in that it does not check that the index returned is within
the bounds of the string. In this case, the pattern `P(2)` is better.

Autoconversion of Values to Patterns
------------------------------------

For convenience, if a :ref:`Pattern` object is combined with another value using
the operators '+', '-', and '*', the other value is converted to a pattern
object using the :ref:`P` class. For example, if ``ptn`` is a pattern, then
``1-ptn`` is equivalent to ``P(1)-ptn``.

.. _match-object:

The Match object
================

As noted above, the :func:`match(string, index=0) <PyPE.PyPE.Pattern.match>` function 
for a pattern is passed a string and an optional index, with the default index of zero
indicating the start of the string. The match function ONLY tests whether the pattern 
is matched at the location indicated by the index. It does not perform a search ahead 
to find a location where the pattern is matched. 

If the pattern matches the string at the given location, a :class:`Match <PyPE.PyPE.Match>` 
object is returned. Otherwise ``None`` is returned. Note that when printing a 
:class:`Match <PyPE.PyPE.Match>` object, the string that was matched by the pattern is 
printed, which is why the pattern examples above print the string that was matched. The 
:class:`Match <PyPE.PyPE.Match>` object also includes the ``start`` and ``end`` location 
of the match, and any Pattern ``captures`` (discussed more below)::

  >>> digit = R('09')**1  # Read one or more digits
  >>> match = digit("01234abc", 1)
  >>> print(match)
  '1234'
  >>> print(match.start)
  1
  >>> print(match.end)
  4
  >>> print(match.captures)  # No captures defined for this pattern
  []

Note that it is easy to create a pattern that does search a string for the given pattern.
For example, suppose that you would like to find the next occurence of a sequence of digits. 
This can be done with the pattern::

  >>> digits = R('09')**1            # Pattern for a sequence of 1 or more digits
  >>> not_digits = (1-digits)**0     # Look for anything but digits (0 or more characters)
  >>> find = not_digits * C(digits)  # Find anything but digits followed by captured digits
  >>> match = find("abc 12345 xq")
  >>> print(match)
  'abc 12345'
  >>> print(match.getCapture(0))
  '12345'

Note that a capture is necessary to retrieve the digits since the ``find``
pattern will match the portion of the string that is not digits as well
(since this is part of the pattern). However, the capture allows us to
retrieve the ``digits`` potion of the pattern. If it is also important to
know the position of the pattern, a position capture ``Cp()`` can be added::

  >>> digits = R('09')**1
  >>> find = (1-digits)**0 * C(Cp()*digits)
  >>> match = find("abc 12345 xq")
  >>> print(match.getCapture(0))      # Print the position at start of capture
  4
  >>> print(match.getCapture(1))      # Print the captured digits 
  '12345'

.. _predefined-patterns:

Predefined Patterns
===================

For convenience, a few commonly used predefined patterns are included in the
PyPE module.

+-----------------+---------------+-------------------------------------------+
| Pattern         | Definition    | Description                               |
+=================+===============+===========================================+
| whitespace      | S(" \\t")     | One space or tab character                |
+-----------------+---------------+-------------------------------------------+
| whitespace0     | whitespace**0 | Zero or more whitespace characters        |
+-----------------+---------------+-------------------------------------------+
| whitespace1     | whitespace**1 | One or more whitespace characters         |
+-----------------+---------------+-------------------------------------------+
| alpha           | R("az", "AZ") | Any lower or upper case letter            |
+-----------------+---------------+-------------------------------------------+
| digit           | R("09")       | Any digit character                       |
+-----------------+---------------+-------------------------------------------+
| newline         | P("\\r\\n") + | Match one new line in unix, windows, or   |
|                 | P("\\r") +    | mac ASCII formats                         |
|                 | P("\\n")      |                                           |
+-----------------+---------------+-------------------------------------------+
| quote           | S("\\"'")     | Match a quote character                   |
+-----------------+---------------+-------------------------------------------+

As an example, the pattern for valid variable names in programming languages
such as c and fortran can be written as::

  >>> var_name = alpha * (alpha + digit + '_')**0
  >>> print(var_name('my_var1 = 5'))
  'my_var1'

.. _capture-ops:

Capture Operators
=================

Captures are used to capture data that is returned from a match. Captures are
added sequentially to a capture array in the order they appear in the pattern.
So for example, if an outer capture contains a set of inner captures, the outer
capture will come before the inner captures in the capture array.

+------------------+-----------------------------------------------------------+
| Operator         | Description                                               |
+==================+===========================================================+
| C(ptn)           | Capture - capture text that matches the specified pattern.|
+------------------+-----------------------------------------------------------+
| Cb(name[,ptn])   | Backcapture - when used as ``Cb(name,ptn)``, try to match |
|                  | pattern ``ptn``. If the match succeeds, store the name and|
|                  | the result of the match. If Cb(name) is used later, try to|
|                  | match the value that was stored earlier. Note that this   |
|                  | does not capture the value to the capture array, but is   |
|                  | merely used to match a value that occurred earlier in the |
|                  | string.                                                   |
+------------------+-----------------------------------------------------------+
| Cc(string)       | Constant capture - Adds the specified string directly to  |
|                  | the capture array.                                        |
+------------------+-----------------------------------------------------------+
| Cg(ptn)          | Group capture - add the capture array from 'ptn' as a     |
|                  | single pattern as a capture value. In other words, the    |
|                  | capture value will be an array.                           |
+------------------+-----------------------------------------------------------+
| Cs(stack[,n,pop])| Stack capture - capture ``n`` values from the specified   |
|                  | stack and pop the values from the stack if ``pop`` is     |
|                  | True. ``n`` is 1 and ``pop`` is False by default.         |
+------------------+-----------------------------------------------------------+
| Cl()             | Line number capture - capture the current line number     |
+------------------+-----------------------------------------------------------+
| Cp()             | Position capture - capture the current string index       |
|                  | (i.e., position).                                         |
+------------------+-----------------------------------------------------------+
| Col()            | Column capture - capture the position on the current line |
|                  | (i.e., the column index).                                 |
+------------------+-----------------------------------------------------------+

The following is an example of a pattern that captures a row of comma separated
integer values on a single line::

  >>> value = whitespace0 * C(digit**1) * whitespace0 # Capture integer value
  >>> row = value * (',' * value)**0  # Capture comma separated list of values
  >>> match = row.match('12, 17, 20, 105')
  >>> print(match.captures)
  ['12', '17', '20', '105']

To capture multiple rows with each capture representing a row, and each capture
containing information about the row the data is on, the following patterns are
added::

  >>> linenum = Cg(Cc("line") * Cl())            # Capture the row rumber
  >>> rows = Cg(linenum * row * newline**-1)**0  # Group together each row of data
  >>> match = rows.match('1,2,3\n4,5,6\n7,8,9')
  >>> print(match.captures)
  [[['line', 1], '1', '2', '3'], [['line', 2], '4', '5', '6'], [['line', 3], '7', '8', '9']]

Backcaptures are not true captures. They are a simple mechanism to match
against a previous match. One applications for this is parsing things like
a quoted string. The following is an example quotes string that captures a
string that starts and ends with the same quote character and does not allow
the string to break across lines::

  >>> quoted = Cb('quote', quote) * (1 - (quote + newline))**0 * Cb('quote')
  >>> print(quoted("'quoted string'"))
  'quoted string'

Using a Function for Type Conversion
------------------------------------

Captures are returned as strings. However, there are cases where it is desirable to
convert the captures to another form. For example, if the capture represents an
integer, it may be useful to convert the value to an integer. The first capture
example above is modified to convert the captured values to integers::

  >>> def str2int(match):
  >>>     match.captures[0] = int(match.captures[0])
  >>>     return match
  >>> toint = C(digit**1) / str2int
  >>> value = whitespace0 * toint * whitespace0
  >>> row = value * (',' * value)**0
  >>> match = row.match('12, 17, 20, 105')
  >>> print(match.captures)
  [12, 17, 20, 105]

The result returned from the function is used as the result of the pattern. In
general, the original match can simply be returned. If the captures in the match
are modified, then the modified results will be used. The ``str2int`` function
above replaces the string of digits captured from the pattern ``C(digit**1)`` 
into an integer value. The result is an array of integer values rather than
an array of integer value strings.

.. _place-holder:

Pattern Place Holder
====================

It is common for a full parsing expression to have to reference patterns 
that have not yet been defined. Or in other words it is common for parsing
expressions to be recursive. When a parsing pattern needs to refer to a 
pattern that has not yet been defined, a pattern place holder can be used
that will later be replaced with the pattern once it is defined. Below are
the 

+--------------------------+------------------------------------------------------------+
| Syntax                   | Description                                                |
+==========================+============================================================+
| V(ptn_name)              | Add a pattern place holder for a pattern that has not yet  |
|                          | been created. This can then be replaced via the ``setVs``  |
|                          | function.                                                  |
+--------------------------+------------------------------------------------------------+
| setVs(ptn, ptn_map)      | Replace the pattern holders in the `ptn` pattern with the  |
|                          | patterns defined in the `ptn_map` mapping object. The      |
|                          | `ptn_map` may either be a dictionary mapping pattern names |
|                          | to patterns, or a list of named patterns (i.e., patterns   |
|                          | that have a name already associated).                      |
+--------------------------+------------------------------------------------------------+
| ptn = <name> | <ptn def> | Create a named pattern. The pipe symbol (\|) is  used to   |
|                          | specify the name for a pattern. The <name> must be a       |
|                          | string value, and <ptn def> represents some pattern        |
|                          | definition. Pattern names are useful for replacing pattern |
|                          | place holders and for pattern debugging.                   |
+--------------------------+------------------------------------------------------------+

As an example, consider a grammar for parsing integer arithmetic expressions of the 
form $5*(2+4)/7$. The grammar might be defined as follows:

  >>> integer = R('09')**1
  >>> op      = S('+-*/')
  >>>
  >>> # An expression needs to refer recursively to itself. Add a placeholder.
  >>> expr    = integer + '-'*V('EXPR') + '('*V('EXPR')*')' + V('EXPR')*op*V('EXPR')
  >>>
  >>> # Replace the expression placeholder in the `expr` pattern
  >>> parse   = setVs(expr, {'EXPR' : expr})
  >>> parse.match("5*(2+4)/7")
  '5*(2+4)/7'

An alternative way to replace the expression is to make `expr` pattern a named pattern. 
The second parameter to `setVs` can be a list of named parameters rather than a dictionary.

  >>> integer = R('09')**1
  >>> op      = S('+-*/')
  >>>
  >>> # Create a named expression
  >>> expr    = 'EXPR' | integer + '-'*V('EXPR') + '('*V('EXPR')*')' + V('EXPR')*op*V('EXPR')
  >>>
  >>> # Send a list of named parameters to replace in `expr`
  >>> parse   = setVs(expr, [expr])
  >>> parse.match("5*(2+4)/7")
  '5*(2+4)/7'


.. _stack-ops:

Stack Operators
===============

A separate capture stack can be useful for storing state, or separation of
concerns when parsing text. The following operations are used to interact with
a stack.

+-----------------------+------------------------------------------------------+
| Operator              | Description                                          |
+=======================+======================================================+
| Sc(name,ptn)          | Capture to stack - capture result of the given       |
|                       | pattern to the a stack identified by the given       |
|                       | ``name``.                                            |
+-----------------------+------------------------------------------------------+
| Sp(name[,n])          | Stack pop - pop n values from the named stack. By    |
|                       | default, n is 1.                                     |
+-----------------------+------------------------------------------------------+
| Sm(name[,n,expected]) | Stack match - If the ``expected`` value is specified |
|                       | with the ``Sm`` operator, then this checks to see if |
|                       | the value at index n in the stack matches the        |
|                       | expected value. This can be used to control parser   |
|                       | logic based on values on the stack. If ``expected``  |
|                       | is not specified, this checks to see if the value at |
|                       | index n in the stack matches the current location in |
|                       | the string passed to ``match``. The default value for|
|                       | n is -1, which indicates the most recent value added |
|                       | to the stack.                                        |
+-----------------------+------------------------------------------------------+
| Ssz(name[,n])         | Stack size - If n is not specified, capture the stack|
|                       | size to the capture array. If n is specified, the    |
|                       | match is only successful if the stack size is n.     |
+-----------------------+------------------------------------------------------+

A simple trivial example of using the stack capability is shown below. Useful
examples that use a stack will typically be more involved::

  >>> stack = Sc('my_stack', Cc('one')*Cc('two'))         # Stack named my_stack with items ['one','two']
  >>> p = stack * Sm('my_stack',0) * ',' * Sm('my_stack') # Look for stack item 0 ('one') -> ',' -> 1 ('two')
  >>> print(p("one,two,three"))
  'one,two'

.. _utility-functions:

Utility Functions
=================

+---------------------------+--------------------------------------------------+
| Function                  | Description                                      |
+===========================+==================================================+
| match(ptn,str,idx)        | Call ``ptn.match(str,idx,ctx)`` where ``str`` is |
|                           | the string to match, and ``idx`` is location in  |
|                           | the string to check for a match.                 |
+---------------------------+--------------------------------------------------+
| matchUntil(ptn, mtchAftr) | Return a pattern that matches anything until     |
|                           | ``ptn`` is matched. ``mtchAftr`` is an optional  |
|                           | parameter that indicates whether ``ptn`` should  |
|                           | be included in the match (default False).        |
+---------------------------+--------------------------------------------------+
| escapeStr(str)            | This function takes a string and replaces \\r,   |
|                           | \\n, and \\t with the string representation, and |
|                           | replaces the quote characters with \' and \".    |
+---------------------------+--------------------------------------------------+
| join(separator)           | This returns a function that can be used with the|
|                           | '/' operator for patterns. This function joins   |
|                           | the captures in a match using the specified      |
|                           | separator. The resulting match has one capture.  |
+---------------------------+--------------------------------------------------+


.. _Tokenizer:

===================
The Tokenizer Class
===================

The :class:`Tokenizer` class is used to create tokenizing parsers, or parsers
which break text into tokens. The :class:`Tokenizer` is constructed from a
grammar, where a grammar is essentially an ordered list of PyPE parsing patterns that
defined the structure of the text. The tokenizer starts at the beginning of a
string and checks the grammar patterns in order until one of the patterns matches
the start of the string. Each of the parsing patterns in the grammar can be given
a name. If the pattern is named, then it is a token and is returned by the
tokenizer along with the :class:`Match` object from the pattern. The tokenizer
then moves to the end of the previous match and repeats the process of checking
for another match of the grammar. This process repeats over and over, returning
tokens as they are found, until the string ends, or none of the patterns in the
grammar match the string at the current location.

Sometimes a single grammar is not sufficient to parse a file. There may be portions
of the file that use a different grammar. The :class:`Tokenizer` supports switching
grammars. A grammar is defined via a list containing the ordered patterns
associated with the grammar. Each grammar is named, and the grammars are specified
in the :class:`Tokenizer` class constructor by passing named parameters with the 
name being the name of the grammar and the value being the list of PyPE patterns 
that defines the grammar. The first parameter passed to the constructor is a string
that indicates the name of the starting grammar. If a string is not passed in, then
the default starting grammar must be named `root`. The :class:`Tokenizer` is 
initialized something like the following:

>>> t = Tokenizer(root=[ptn1, ptn2, ptn3, ...], other=[optn1, optn2, optn3, ...], ...)

The tokenizer can then be used to parse one or more strings. This is done by calling
the :func:`getTokens` function and passing it the string to parse as shown below:

>>> for token, match in t.getTokens(string):
>>>   # do something with the token and associated match object

This tokenizer can then be called with a different string to parse that string
as well. Note that each pattern needs to consume part of the string, or the
parser will not progress. If a pattern succeeds, but does not consume any text
from the string (i.e., is length 0) then the parser will stop.

In order for multiple grammars to be useful, there needs to be a way to 
switch to a new grammar. This is done by including a tuple with three values in the
grammar list (a tuple is a list included in parenthesis). The first value in the
tuple is a pattern that marks the start of the new grammar. The second value in
the tuple is the string name of the new grammar. The third value is a pattern that
marks the end of the grammar. If the new grammar does not end, then the third value
is not required. 

>>> t = Tokenizer(root=[ptn1, ptn2, (P('['), 'other', P(']'))], other=[optn1, optn2, optn3])

In this case, the tokenizer switches from the ``root`` grammar to the ``other`` grammar if
``ptn1`` and ``ptn1`` fail at the current location in the string and the string contains
an opening square bracket at this location. This means that the start grammar pattern
matches. Note that the pattern above will consume the square bracket, so the ``other``
pattern should not include the square bracket. While patterns in a grammar must
consume part of the string, the start grammar pattern can be a look ahead pattern
that does not consume any text. However, the combination of the start pattern, the
new grammar, and the end pattern must consume some text from the string, or the
tokenizer will stall and end. When a new grammar ends, then parent grammar begins
to parse again. Grammars can be nested multiple layers deep.

As noted above, only named patterns from a grammar are returned as tokens. A pattern
can be named using the following:

>>> ptn.name = "<name>"

However, the pipe operator (``|``) is overloaded for patterns, so a more convenient
way to name a pattern is:

>>> ptn = "<name>" | pattern_definition

Below is an example of a parser the tokenizes works until an open parenthesis is
encountered. Then it tokenizes numbers until a close parenthesis is encountered.
It then starts tokenizing words again.

.. literalinclude:: /../TokenizerExample.py
   :language: python

The output from this script is the following:

.. highlight:: none
::

    word: cat
    word: rat 
    open: (   
    number: 11
    number: 12
    number: 13
    close: )  
    word: bat
    
It is worth emphasizing that ``match`` is a :class:`Match` object, which can include
capture values. The match captures can be quite sophisticated depending on the
token patterns that are defined in the grammars, and may cover significant portions
of the text.

.. _Template:

==================
The Template Class
==================

A template file is a text file written in a file format that embeds scripting
tags for dynamic content creation. The scripting language used in the scripting 
tags is python. When the template file is rendered, it may be passed a set of 
template variables that are used within the template.

The syntax used for scripting tags in a template file is ``@[<python code>]@``,
where the tag may be on a single line, or the python code may span multiple lines.
The tag syntax includes some optional modifiers, with the optional modifiers shown
below in parenthesis and exclusive options delineated with the ``'|'`` symbol. The
extended syntax is::

    @[(^)(=|>|<)(:*) <python code> (^)]@

Note that no space is allowed between the start or end of the tag and the
modifiers used. The ``^`` symbol, which can be used at the start or the
end of the tag is meant to look like an up arrow and indicate that a newline and
whitespace that occurs either before or after the script tag (depending on where
the ``^`` is used) should be removed.

The script tag may also contain one of ``=``, ``>``, or ``<`` at the
start of the tag. 

* The ``=`` indicates that the python code is a variable or a
  function call and that the result should be written to the LaTeX document in
  place of the tag. 
* The ``>`` and ``<`` tags also cause the value to the written to the file. 
  However, in this case, the text will take up the same length as the tag if 
  possible, adding whitespace as needed. The ``>`` and ``<`` symbols are used to 
  indicate right or left alignment of the text respectively. If the value being 
  printed is longer than the tag, then the value is printed without modification.

Finally, zero or more ``:`` characters may be included just before the python
code. To understand the purpose of the colons, it is important to understand how
python scripts are organized. Python includes a few statements that are used to
organize and control a script. Structures used to control the flow of a script
include functions, ``if`` statements, ``for`` loops, among others. Each
control structure includes a block of code. In python, a control structure must
be followed by a colon, which marks the start of the block of code. The colon
may be followed by a statement on the same line, in which case the block ends
with the end of the line. Otherwise if the control statement line ends with a
colon (possibly followed by a comment), the block of statements contained in the
must be indented past the control statement and all statements indented to the
same level are part of the same block until the code is unindented or ends.
While indentation works well to organize code blocks in a python script, this
implicit approach to marking the end of a block does not work for a template.
Thus the number of colons at the start of a tag mark the number of blocks that
have been closed. Below is an example::

  @[ debug = True
     if debug == True:
        if verbose == True: ]@
    This is my verbose message. It is not necessary to indent this text.
  @[ :else: ]@
    This is my nonverbose message.

    Because of the single colon before the else, this 'else' statement is for the
    'if verbose' command. If two colons were used it would be for the 'if debug'
    command. Note that the 'else' statement ends with a ':' which means that
    a new block is started for the else statement.
  @[ :: # Exit the 'else' and 'if debug' blocks ]@

Note that the template only detects a new block if the line ends with a colon.
The template will not detect a line that ends with a colon followed by a comment
at the end of the line. The following are some example tags::

  @[ x = "testing" ]@ - Set the value for variable x
  @[= x ]@            - Print the variable x
  @[^= x ]@           - Print x and remove whitespace and newline before value
  @[ myfn() ]@        - Call the function 'myfn'
  @[= myfn() ]@       - Call the function 'myfn' and include return value in LaTeX
  @[> testing ]@      - The tag is 14 characters, so this will take up at least
                        14 characters and will be right aligned.

A function that is called may write content to the output even if it does not
return a value. Documentation on how to create new functions and write to the
output is presented in :ref:`TemplateFns`. If a tag is used that writes
output (such as ``@[=myfn()]@``), and the value is empty (such as a function
that does not return a value), then the empty value is ignored.

When a template file is processed, it is converted into a python script with the
same name as the template file, but with the extension changed to '.py', and
located in a folder named ``temp`` created in the folder where the script is executed. 
Thus, using repeat names for files that are included in subdirectories is not 
allowed. If the template has syntax errors, the python file that is created may 
not run correctly. Some sytax errors may be reported while compiling the template
file. If the template is compiled to a python file, then examining the python
file that is created in the ``temp`` folder is another way to diagnosing errors.

Since the template files are converted to standard python files before they are
executed, it is possible to run the files in a python IDE for debugging if the
templates are producing incorrect output. This can be a fast and effective method
of determining why results are not correct. There are a number of good python IDEs.
One of the simplest to setup and use is Visual Studio Code, which is free to download 
and use. Python 3 must be installed on your system and the Visual Studio Code Python
extension must be added for python debugging to work.

To render the document, a :class:`Template` object is created and is passed the
name of the template file. The template can then be rendered. Variables that are
used in the template can be passed to the render function as shown below:

.. highlight:: default
::

  t = Template("Temp", readFile=False)
  t.addPythonFunction(src)
  t.addTemplateFunctions(sys.modules[__name__])     # Load TemplateFn from this file
  print(t.render({'name':"fred", 'a':"A Value"}))
  
Note that :func:`render` returns a string, which can be printed or written to
a file.
  
.. _TemplateFns

Variables and Functions Available within Templates
==================================================

A few variables and functions are available for use within a template file.
Some of these are added from the ``Template.py`` module, but most are implemented
in the ``TemplateFunction.py`` file. The following is a table of the variables and
functions that are available:

+------------------------+-----------------------------------------------------+
|          Name          |                     Description                     |
+========================+=====================================================+ 
| __stack__              | This is the array that stores the output that is    |
|                        | written before it is joined together into a final   |
|                        | document. It is not usually necessary to use this   |
|                        | directly. This variable should not be redefined.    |
+------------------------+-----------------------------------------------------+
| write(value)           | This function is used to write template output. This| 
|                        | function is used in the template code that is       |
|                        | generated, and the function should not be redefined.|
+------------------------+-----------------------------------------------------+
| writeln(value)         | Similar to the ``write`` function, but includes a   |
|                        | newline after the content that is written to the    |
|                        | output.                                             |
+------------------------+-----------------------------------------------------+

.. _TemplateFns:

Template Functions
==================

While the template syntax allows arbitrary python code to be included in a template
file, it is recommended that the templates only include minimal code logic. If 
multiple lines of code logic are required, it is better to add a new template 
function to the ``TemplateFunction.py`` file in the ``scripts`` directory.

The ``TemplateFunction.py`` script imports and decorator function called
``TemplateFn`` from ``PyPE.Template``. In order to mark a function in this script
as a function that should be available within the templates, ``@TemplateFn``
must be added on the line before the function is defined. The following is an
example of declaring a function that can be called from a template.::

    @TemplateFn
    def aUselessFunction():
      return "a dummy string"

The function can receive any parameters that are needed to perform its job. 
When a template is called, a ``context`` variable is added to the function that 
contains all of the parameters passed to the Template. This is not passed directly, 
but is set as a function property. In general, it is recommended that any 
parameters that are needed be passed to a function directly, but if there is a 
case where this is particularly inconvenient, the ``context`` variable can be used. 
The context can be accessed via the function name as follows::

    @TemplateFn
    def myfn():
      context = myfn.context
      writeln = context.writeln   # Function to write directly to latex
      writeln('This is written directly to the text output')

The code in ``TemplateFunction.py`` is standard python code, so the developer is
free to implement any logic necessary for documentation purposes. Template functions
must be registered with the :class:`Template` prior to rendering the template in
order to be accessible. Templates are registered by calling the function
:func:`addTemplateFunctions` on the template and passing it a module or a
class object that contains template functions. Note that if template functions are
contained in a class, a class object must be passed to :func:`addTemplateFunctions` 
and not the class itself. If the template functions are contained in the script 
that is executed, the following can be used to pass the script for registering 
template functions::

    import sys
    ...
    t = Template(filename)
    t.addTemplateFunctions(sys.modules[__name__])

Sometimes it may be useful to generate a template from a string rather than a
file file. In this case, the template can be initialized with the second parameter
``readFile`` being ``False``. The first parameter is still the basename to use
for the python template that is generated. In this case, the template string can
be passed to :func:`addPythonFunction`. Below is an example script that generates
a template from a string and registers a template function included in the script.

.. literalinclude:: /../TemplateExample.py
   :language: python
   
The result from the script is the following:

.. highlight:: none
::

    Text should be added as is
    The write function is availabe in Templates
    fred
    Newlines must be added explicitly with write

    Variables can be created on the fly. For the block below, unindent
    the if statement above and set a few variables. Remove the return value
    at the end of this below so that no empty line shows up in the rendered
    text.
    Values can be written out. Remove the newline at the start of the block
    below: 5
    # The size of a code block can be preserved
    #          make this string right aligned. Remove the newline at the start and end.

    This is from the TemplateFn

==================
Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. toctree::
  :maxdepth: 2

  PyPE.rst
