PyPE (Python Parsing Expressions) Library
=========================================

PyPE is a python pattern matching library for searching text and extracting 
data from the text. While PyPE can be used to match text patterns in any text 
file, it is particularly useful for interpreting structured text and converting 
the text into data structures that can be used in a program. Examples of text 
with structure are html or xml documents, comma separated value or tab delimited 
files, or source code files. The code used to interpret structured text and 
convert it to data structures is referred to as a parser. PyPE is used to create 
a specific type of parser called a parsing expression grammar (PEG).

A parsing expression grammar is used to represent the structure of a text 
document in a way that allows the document to be parsed. PEGs are similar in 
purpose to regular expressions. PEGs tend to be more verbose than regular 
expressions, but when well written are often easier to interpret. PEGs are also 
more flexible than regular expressions and can be used to parse complex recursive 
grammars such as programming languages. While PEGs are more powerful than regular 
expressions, they are argueably also often easier to write.

Parsing expressions use a declarative programming style, where the structure of 
a text input is defined and the information to capture is specified without 
indicating how the text input will be processed. Once the syntax of the text 
input is described, the PEG parser can be passed a string and will return the 
data extracted from the string in a data structure that can be used in the 
program or can be converted into a form needed within the program.

PyPE is modeled after the Lua LPEG (Lua Parsing Expression Grammars) library. 
The syntax has been preserved where possible, although some of the operators in 
Python use a different syntax than Lua and not all of the operations of LPEG 
are included, and some additional features that are not part of LPEG are added. 
For example, support for debugging a grammar is built into PyPE.

*Documentation for PyPE can be found at: [https://llarsen.bitbucket.io/PyPE/](https://llarsen.bitbucket.io/PyPE/)*


