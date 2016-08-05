#===============================================================================
# MIT license
#
# Copyright (c) 2016 Lance Larsen
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#===============================================================================
#
# PyLPEG is a pure python parsing expression grammars library designed to mimic
# the Lua LPEG library. Syntax is made to be consistent were possible.
#
#===============================================================================

class Pattern(object):

  #-----------------------------------------------------------------------------

  def __init__(self):
    pass

  #-----------------------------------------------------------------------------

  def match(self, string, index=0):
    return False

  #-----------------------------------------------------------------------------

  @staticmethod
  def isMatch(index, strlen, start_index):
    """
    Check whether the index indicates a valid match.
    """
    # For some reason 'index == False' evaluates to True if 'index == 0'.
    # so we check for a boolean
    if isinstance(index, bool) and index == False: return False
    if index < start_index or strlen < index: return False
    return True

  #-----------------------------------------------------------------------------

  @staticmethod
  def positiveIndex(string, index, msg="Invalid index"):
    """
    Get the string index as a positive value. A negative index is calculated
    from the end of the string. If the index is outside the string bounds, an
    Exception is raised if msg is set. Otherwise the index at start or end of
    the string is returned.
    """
    sz = len(string)
    if index >= 0:
      if index > sz and msg: raise ValueError(msg)
      return sz if index > sz else index

    idx = sz - index
    if idx < 0 and msg: raise ValueError(msg)
    return 0 if idx < 0 else idx

  #-----------------------------------------------------------------------------

  def __mul__(self, other):
    """
    Suport 'ptn*a'
    """
    if isinstance(other, PatternAnd):
      other.prependPattern(self)
    return PatternAnd(self, other)

  #-----------------------------------------------------------------------------


  def __rmul__(self, other):
    """
    Support 'a*ptn'
    """
    if isinstance(other, PatternAnd):
      other.appendPattern(self)
    return PatternAnd(other, self)

  #-----------------------------------------------------------------------------

  def __add__(self, other):
    """
    Support 'ptn+a'
    """
    if isinstance(other, PatternOr):
      other.prependPattern(self)
      return
    return PatternOr(self, other)

  #-----------------------------------------------------------------------------

  def __radd__(self, other):
    """
    Support 'a+ptn'
    """
    if isinstance(other, PatternOr):
      other.appendPattern(self)
      return
    return PatternOr(other, self)

  #-----------------------------------------------------------------------------

  def __sub__(self, other):
    """
    Support 'ptn-a'
    """
    return PatternAnd(PatternNot(other), self)

  #-----------------------------------------------------------------------------

  def __rsub__(self, other):
    """
    Support 'a-ptn'
    """
    return PatternAnd(PatternNot(self), other)

  #-----------------------------------------------------------------------------

  def __neg__(self):
    """
    Support '-ptn'
    """
    return PatternNot(self)

  #-----------------------------------------------------------------------------

  def __xor__(self, n):
    """
    Support ptn^n to get at least n repeats of pattern.
    """
    return PatternRepeat(self, n)

  #-----------------------------------------------------------------------------

  def __call__(self, string, index=0):
    return self.match(string, index)

#===============================================================================

class PatternRepeat(Pattern):

  #-----------------------------------------------------------------------------

  def __init__(self, pattern, n):
    if not isinstance(pattern, Pattern): raise ValueError("First value to PatternRepeat must be a pattern")
    if not isinstance(n, int): raise ValueError("In ptn^n, n must be an integer value")
    self.pattern = pattern

    if n >= 0:
      self.match = self.match_at_least_n
      self.n = n
    else:
      self.match = self.match_at_most_n
      self.n = -n

  #-----------------------------------------------------------------------------

  def match_at_least_n(self, string, index=0):
    """

    >>> p = S("abc")^3
    >>> p("ab")
    False
    >>> p("abc")
    3
    >>> p("abcabcd")
    6
    """
    cnt = 0
    while True:
      new_index = self.pattern.match(string, index)

      # No progress, so it matches infinite times
      if index == new_index: return index
      if not self.isMatch(new_index, len(string), index):
        return index if cnt >= self.n else False

      cnt += 1
      index = new_index

  #-----------------------------------------------------------------------------

  def match_at_most_n(self, string, index=0):
    """

    >>> p = S("abc")^-3
    >>> p("")
    0
    >>> p("abca")
    3
    """

    new_index = index
    for i in range(self.n):
      new_index = self.pattern.match(string, index)
      if new_index == False: return index
      index = new_index
    return new_index

  #-----------------------------------------------------------------------------

  def __repr__(self):
    return "%s^%s" % (repr(self.pattern), self.n)

#===============================================================================

class P(Pattern):

  #-----------------------------------------------------------------------------

  def __init__(self, value):
    self.isValidValue(value)

    if isinstance(value, Pattern):
      self.match  = self.match_ptn
      self.ptn    = value
      self.repr   = "P(ptn)"

    if isinstance(value, basestring):
      self.match  = self.match_str
      self.string = value
      self.size   = len(value)
      # TODO: Handle signle quotes in representation.
      self.repr   = "P('%s')" % value

    elif isinstance(value, bool):
      self.match  = self.match_TF
      self.TF     = value
      self.repr   = "P(%s)" % value

    elif isinstance(value, int):
      if value >= 0:
        self.match  = self.match_n
        self.n      = value
      else:
        self.match  = self.match_neg
        self.n      = -value
      self.repr     = "P(%s)" % value

    elif callable(value):
      self.match  = self.match_fn
      self.fn     = value
      self.repr   = "P(fn)"

  #-----------------------------------------------------------------------------

  @staticmethod
  def isValidValue(value, msg = "Invalid arg for P(arg)"):
    """
    Veify that P(arg) is a valid arg. Raise an exception if not.
    """
    if isinstance(value, (Pattern, basestring, bool, int)): return True
    if callable(value): return True
    raise ValueError(msg)

  #-----------------------------------------------------------------------------

  @staticmethod
  def asPattern(pattern):
    """
    If item is a pattern, return the pattern. Otherwise return P(pattern)
    """
    return pattern if isinstance(pattern, Pattern) else P(pattern)

  #-----------------------------------------------------------------------------

  def match_ptn(self, string, index=0):
    """
    Matches the pattern passed in.

    >>> p = P(P("ab"))
    >>> p("abba")
    2
    >>> p("abba",1)
    False
    """
    return self.ptn(string, index)

  #-----------------------------------------------------------------------------

  def match_str(self, string, index=0):
    """
    Matches an exact string

    >>> p = P("test")
    >>> p("testing")
    4
    >>> p("A test",2)
    6
    >>> p("None")
    False
    """
    if len(string) - index < self.size: return False
    if string[index:index+self.size] == self.string: return index + self.size
    return False

  #-----------------------------------------------------------------------------

  def match_n(self, string, index=0):
    """
    Matches exactly n characters.

    >>> p = P(1)
    >>> p("")
    False
    >>> p("a")
    1
    >>> p = P(3)
    >>> p("ab")
    False
    >>> p("abc")
    3
    >>> p("abc",1)
    False
    """
    if len(string) - index < self.n: return False
    return index + self.n

  #-----------------------------------------------------------------------------

  def match_neg(self, string, index=0):
    """
    Matches less than n characters only (end of string).

    >>> p = P(-3)
    >>> p("")
    0
    >>> p("ab")
    2
    >>> p("abc")
    False

    """
    sz = len(string)
    if sz - index >= self.n: return False
    return sz

  #-----------------------------------------------------------------------------

  def match_TF(self, string, index=0):
    """
    Return False if the value is False, or the 'index' value if not past end of
    string.

    >>> p = P(False)
    >>> p("test")
    False
    >>> p = P(True)
    >>> p("test")
    0
    >>> p("test",3)
    3
    >>> p("test",5)
    False
    """
    if not self.TF or index > len(string): return False
    return index

  #-----------------------------------------------------------------------------

  def match_fn(self, string, index=0):
    """
    Call the function with the string and the index value. If the function returns
    an integer between the index value and the length of the string, return this
    value. If the function returns True, return index. Otherwise, return False.

    >>> p = P(lambda str, i: i+2)
    >>> p("test")
    2
    >>> p("test",3)
    False
    >>> p = P(lambda str, i: True)
    >>> p("test",4)
    4
    """
    new_index = self.fn(string, index)
    if self.isMatch(new_index, len(string), index): return new_index
    if new_index == True: return index
    return False

  #-----------------------------------------------------------------------------

  def __repr__(self):
    return self.repr

#===============================================================================

class S(Pattern):
  """
  Match any of a given set of characters.
  """

  #-----------------------------------------------------------------------------

  def __init__(self, set):
    if not isinstance(set, basestring):
      raise ValueError("The arg must be a string in S(arg)")
    self.set = set

  #-----------------------------------------------------------------------------

  def match(self, string, index=0):
    """
    Match character in the given set.

    >>> p = S("ace")
    >>> p("a")
    1
    >>> p("b")
    False
    >>> p("abc",2)
    3
    """
    if len(string) - index < 1: return False
    if string[index] not in self.set: return False
    return index + 1

  #-----------------------------------------------------------------------------

  def __repr__(self):
    # TODO: Handle single quote in set
    return "S('%s')" % self.set

#===============================================================================

class R(Pattern):
  """
  Match characters in a given range.
  """

  #-----------------------------------------------------------------------------

  def __init__(self, *ranges):
    self.ranges = ranges
    for range in ranges:
      if len(range) != 2: raise ValueError("Ranges must have two values: %s" % value)
      if range[0] > range[1]: raise ValueError("Lower range value must be less than upper range value: %s" % value)

  #-----------------------------------------------------------------------------

  def match(self, string, index=0):
    """
    Matches any character in the given set of ranges.

    >>> p = R("AZ","az")
    >>> p("a")
    1
    >>> p("Q")
    1
    >>> p("1")
    False
    """
    if len(string) - index < 1: return False

    chr = string[index]
    for range in self.ranges:
      if range[0] <= chr and chr <= range[1]: return index+1
    return False

  #-----------------------------------------------------------------------------

  def __repr__(self):
    # TODO: Handle single quote in range values
    return "R(%s)" % (",".join(["'%s'" % range for range in ranges]))

#===============================================================================
# Pattern Operators
#===============================================================================

class PatternAnd(Pattern):
  """
  Look for the first pattern in the list that matches the string.
  """

  #-----------------------------------------------------------------------------

  def __init__(self, pattern1, pattern2):
    if not isinstance(pattern1, Pattern) and not isinstance(pattern2, Pattern):
      raise ValueError("PatternAnd requires the first or second constructor item to be a Pattern")

    isValidValue = P.isValidValue
    isValidValue(pattern1, msg="For 'a*b', 'a' must be Pattern or int value")
    isValidValue(pattern2, msg="For 'a*b', 'b' must be Pattern or int value")

    asPattern = P.asPattern
    self.patterns = [asPattern(pattern1), asPattern(pattern2)]

  #-----------------------------------------------------------------------------

  def appendPattern(self, pattern):
    """
    Add a pattern to the end of the or list
    """
    self.patterns.append(P.asPattern(pattern))

  #-----------------------------------------------------------------------------

  def prependPattern(self, pattern):
    """
    Add a pattern to the start of the or list
    """
    self.patterns.insert(0, P.asPattern(pattern))

  #-----------------------------------------------------------------------------

  def match(self, string, index=0):
    """
    Find the first pattern that matches the string.

    >>> p = P("bob ") * P("bill ") * P("fred")
    >>> p("bob bill fred")
    13
    >>> p("bob bill fran")
    False
    >>> p = P("tes") - P("test")
    >>> p("tesseract")
    3
    >>> p("testing")
    False
    """

    # Make sure all the patterns match
    for pattern in self.patterns:
      next_index = pattern.match(string, index)
      if not self.isMatch(next_index, len(string), index): return False
      index = next_index
    return index

  #-----------------------------------------------------------------------------

  def __mul__(self, other):
    """
    Support 'ptn*a'
    """
    self.appendPattern(other)
    return self

  #-----------------------------------------------------------------------------

  def __rmul__(self, other):
    """
    Support 'a*ptn'
    """
    self.prependPattern(other)
    return self

  #-----------------------------------------------------------------------------

  def __sub__(self, other):
    """
    Support 'ptn-a'
    """
    self.prependPattern(PatternNot(other))
    return self

  #-----------------------------------------------------------------------------

  def __repr__(self):
    from itertools import takewhile

    # Get the pattern from inside the PatternNot object since we will add '-' manually
    nots = [item.pattern for item in takewhile(lambda item: isinstance(item, PatternNot), self.patterns)]

    # If there are nots at the start, write as a*b - c - d ...
    if len(nots) > 0:
      n = len(nots)
      ands = "*".join([repr(pattern) for pattern in self.patterns[n:]])
      nots.reverse()
      nots = " - ".join([repr(item) for item in nots])
      return "%s - %s" % (ands, nots)

    return "*".join([repr(pattern) for pattern in self.patterns])

#===============================================================================

class PatternOr(Pattern):
  """
  Look for the first pattern in the list that matches the string.
  """

  #-----------------------------------------------------------------------------

  def __init__(self, pattern1, pattern2):
    if not isinstance(pattern1, Pattern) and not isinstance(pattern2, Pattern):
      raise ValueError("PatternOr requires the first or second constructor item to be a Pattern")

    isValidValue = P.isValidValue
    isValidValue(pattern1, msg="For 'a+b', 'a' must be Pattern or int value")
    isValidValue(pattern2, msg="For 'a+b', 'b' must be Pattern or int value")

    asPattern = P.asPattern
    self.patterns = [asPattern(pattern1), asPattern(pattern2)]

  #-----------------------------------------------------------------------------

  def appendPattern(self, pattern):
    """
    Add a pattern to the end of the or list
    """
    self.patterns.append(P.asPattern(pattern))


  #-----------------------------------------------------------------------------

  def prependPattern(self, pattern):
    """
    Add a pattern to the start of the or list
    """
    self.patterns.insert(0, P.asPattern(pattern))

  #-----------------------------------------------------------------------------

  def match(self, string, index=0):
    """
    Find the first pattern that matches the string.

    >>> p = P("bob") + P("bill") + P("fred")
    >>> p("obob",1)
    4
    >>> p("duck bill",5)
    9
    >>> p("fred")
    4
    >>> p("none")
    False
    """

    for pattern in self.patterns:
      next_index = pattern.match(string, index)

      if self.isMatch(next_index, len(string), index):
        return next_index
    return False

  #-----------------------------------------------------------------------------

  def __add__(self, other):
    """
    Support 'ptn+a'
    """
    self.appendPattern(other)
    return self

  #-----------------------------------------------------------------------------

  def __radd__(self, other):
    """
    Support 'a+ptn'
    """
    self.prependPattern(other)
    return self

  #-----------------------------------------------------------------------------

  def __repr__(self):
    return " + ".join([repr(pattern) for pattern in self.patterns])

#===============================================================================

class PatternNot(Pattern):
  """
  Verify that the text ahead does not match the pattern. The string index does
  not advance.
  """

  #-----------------------------------------------------------------------------

  def __init__(self, pattern):
    P.isValidValue(pattern, msg ="Invalid '-ptn' expression")
    self.pattern = P.asPattern(pattern)

  #-----------------------------------------------------------------------------

  def match(self, string, index=0):
    """

    >>> p = -P("bob")
    >>> p("bob")
    False
    >>> p("fred")
    0
    """

    new_index = self.pattern(string, index)
    if not self.isMatch(new_index, len(string), index): return index
    return False

  #-----------------------------------------------------------------------------

  def __repr__(self):
    return "-%s" % repr(self.pattern)

#===============================================================================

def match(pattern, subject, index=0):
  """
  """
  pass

#===============================================================================

if __name__ == "__main__":
  import doctest
  doctest.testmod()
