.. _PyPE-intro:

========================
PyPE - API Documentation
========================

-------------------------------
The :class:`Pattern` Base Class
-------------------------------

:class:`Pattern <PyPE.PyPE.Pattern>` is an abstract base class for all pattern 
objects. The most important function for patterns is 
:func:`match(string[, index]) <PyPE.PyPE.Pattern.match>`, which checks 
a string starting at the given index to see if it matches the pattern. A 
:class:`Match <PyPE.PyPE.Match>` object is returned if a match is found, or 
``None`` if the pattern did not match the string at the given index. Each 
subclass of :class:`Pattern <PyPE.PyPE.Pattern>` implements different search
patterns. Note that for convenience the pattern object can be called as if it 
is a function, and the call is forwarded to :func:`match`. Therefore, if
``ptn`` is a pattern, the following are equivalent::

  >>> match = ptn.match("This is a test")
  >>> match = ptn("This is a test")

A :class:`Match <PyPE.PyPE.Match>` object allows you to get the string that
was matched and any captures. It also includes a ``context`` value that 
provides access to any :class:`Stack` objects that were created. Some patterns
may succeed without consuming any values from the string. To avoid infinite loops
in a parsing expression, some care must be taken to ensure that no recursive 
expressions occur that consume no text. For reference, this is referred to as "left recursion" 
in PEG literature, and grammars can be rewritten to remove "left recursion".
Information on this can be found via an internet search.

Any pattern can be 'named' by calling :func:`setName <PyPE.PyPE.Pattern.setName>` 
for the pattern or by using the 'set name' operator (shown later). This is 
primarily used for debugging purposes or when building a :class:`Tokenizer`, 
since all token patterns must have a name specified.

Debug mode can be set for any pattern by calling the function 
:func:`debug <PyPE.PyPE.Pattern.debug>` with ``True`` (to debug all subpatterns), 
``False`` (to supress debug message for a pattern and subpatterns]), and 
``"named"`` (to show only named patterns in the debug output).

.. _Pattern:

Pattern
=======

.. autoclass:: PyPE.PyPE.Pattern
   :members:

-----------------
Pattern Operators
-----------------

.. _P:

P (Pattern)
===========

.. autoclass:: PyPE.P
   :members:

I (Ignore Case)
===============

.. autoclass:: PyPE.I
   :members:

S (Set)
=======

.. autoclass:: PyPE.S
   :members:

R (Range)
=========

.. autoclass:: PyPE.R
   :members:

SOL (Start of Line)
===================

.. autoclass:: PyPE.SOL
   :members:

   
EOL (End of Line)
=================

.. autoclass:: PyPE.EOL
   :members:

-----------------
Capture Operators
-----------------
   
C (Capture)
===========

.. autoclass:: PyPE.C
   :members:
   
Cb (Backcapture)
================

.. autoclass:: PyPE.Cb
   :members:

Cc (Contstant Capture)
======================
   
.. autoclass:: PyPE.Cc
   :members:

Cg (Group Capture)
==================

.. autoclass:: PyPE.Cg
   :members:

Cs (Stack Capture)
==================

.. autoclass:: PyPE.Cs
   :members:

Cl (Line number Capture)
========================
   
.. autoclass:: PyPE.Cl
   :members:

Cp (Position Capture)
=====================
   
.. autoclass:: PyPE.Cp
   :members:

Col (Column Capture)
====================
   
.. autoclass:: PyPE.Col
   :members:

---------------
Stack Operators
---------------

Sc (Capture to Stack)
=====================

.. autoclass:: PyPE.Sc
   :members:

Sm (Stack Match)
================

.. autoclass:: PyPE.Sm
   :members:

Ssz (Stack Size)
================

.. autoclass:: PyPE.Ssz
   :members:

.. _Match:

-------------
Match Objects
-------------

A ``Match`` object is returned when the :func:`match(string, index) <PyPE.PyPE.Pattern.match>`
function for a pattern is called with a string, and the string matches the
pattern at the given index. The ``Match`` object indicates the portion of the
string that was matched, the start and end location of the match, and contains
any captures from the pattern.

Match
=====

.. autoclass:: PyPE.PyPE.Match
   :members: