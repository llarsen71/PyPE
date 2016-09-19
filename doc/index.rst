.. toctree::
   :maxdepth: 2


PyPE's (Python Parsing Expressions)
===================================

PyPE is a python library for building parsers. A parser takes text input and
converts the text to a data structure that represents the original text input in
a form that is more convenient for use in a program. PyPE is modeled after the
Lua LPEG (Lua Parsing Expression Grammars) library. The syntax has been preserved
where possible, although some of the operators in Python use a different syntax
than Lua and not all of the operations of LPEG are included, and some additional
features that are not part of LPEG are added. For example, support for debugging
a grammar is built into PyPE.

Parsing expressions use a declarative programming style, where the structure of
a text input and the information to capture is defined without indicating how
the text input will be processed. Once the syntax of the text input is
described, the parser handles the processing of the file and return the
information from the text input that is indicated in the parser.



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

PyPE Module
===========

.. automodule:: PyPE.PyPE
