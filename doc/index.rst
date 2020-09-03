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

* :ref:`stack-ops` - A stack is just a named array that works similar to the
  capture array. In some cases, it is useful to add captured data to a stack
  that is independent of the capture array.

* :ref:`utility-functions` - Other functions that can be used with PEGs.

To check if a string matches a pattern defined using PyPE, the patterns
``match`` function is called. If the string is a match a ``Match`` object
is called. This is discussed in :ref:`match-object`.

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
|             | string length.                                                 |
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

For convenience, if a :ref:`Pattern` object is combined with another value using
the operators '+', '-', and '*', the other value is converted to a pattern
object using the :ref:`P` class. For example, if ``ptn`` is a pattern, then
``1-ptn`` is equivalent to ``P(1)-ptn``.

The following is an example of a simple pattern that can be used to check for
a digit::

  >>> digit = R('09')  # Read characters in the range 0-9

This pattern matches only a single digit. A string can be checked to see if it
matches the pattern by calling the pattern's match function::

  >>> match = digit.match('56a7')
  >>> print(match)
  '5'

The :func:`match <PyPE.PyPE.Pattern.match>` function accepts a string and an
optional location in the string to look for a match (with the default being
0 which indicates the start of the string). If the index 2 is used, the match
fails because the character at index 2 is 'a'.

  >>> digit.match('56a7',2) == None
  True

The pattern can be extended to read one or more digits as follows::

  >>> digits = R('09')**1
  >>> match = digits('56a7')
  >>> print(match)
  '56'

The following is an example of a pattern that finds any one of three different
ways of representing a new line in a text file::

  >>> newline = P('\r\n') + P('\r') + P('\n')

Note that this is an order search, meaning that if ``newline.match(string)`` is
called, the ``newline`` pattern checks if the string starts with the first expression 
``P('\r\n')``, and if this fails to match, the ``newline`` pattern checks if the
string starts with the second pattern ``P('\r')``. If this fails to match, the third 
pattern ``P('\n')`` is tested. If any of the three patterns succeeds, then the matched
characters are returned. However, if all patterns fail, the returned result is ``None``.

Note that the ordering of the pattern matters. For example, the following pattern will never
return the result ``\r\n`` because ``\r`` will always be matched first.

  >>> newline = P('\r') + P('\r\n') + P('\n')

Patterns can be combined to make more complex expressions::

  >>> anything_but_newline = 1-newline  # Match anything with the exeption of newline
  >>> to_end_of_line = anything_but_newline**0 * newline**-1
  >>> print(to_end_of_line.match("123\n456")) # Note newline is included in match
  '123'

  >>> print(to_end_of_line.match("123\n456", 4)) # Matches end of string with no newline
  '456'

The ``to_end_of_line`` pattern can be read as 'Match zero or more of anything
but newline, followed by at most one newline'.

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
  >>> print(math.captures)  # No captures defined for this pattern
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
  ['12', '17', '20', 105']

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


==================
Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. toctree::
  :maxdepth: 2

  PyPE.rst
