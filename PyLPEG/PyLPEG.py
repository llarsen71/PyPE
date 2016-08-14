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

def ConfigBackCaptureString4match(fn):
  """
  Wrap string as a BackCaptureString and clear backcaptures on failed matches.
  """
  def match(matchObj, string, index=0):
    if not isinstance(string, BackCaptureString): string = BackCaptureString(string)
    sz = string.getStackSize()

    debug = olddebug = string.debug()
    if matchObj.debug() is not False:
      debug = matchObj.debug()
      string.debug(debug)
    debug = debug and not (debug is Pattern.NAMED and matchObj.name is None)

    if debug:
      name = matchObj.name or repr(matchObj)
      print "Enter: ({0}) {1}".format(index, name)

    matchResult = fn(matchObj, string, index)

    if debug:
      if not isinstance(matchResult, Match):
        print "Leave: ({0}) {1}".format(index, name)
      else:
        print "Result: ({0}) {1}".format(index, name)
        print "        {0}".format(str(matchResult))

    if not isinstance(matchResult, Match):
      string.setStackSize(sz)

    # restore the debug state
    string.debug(olddebug)

    return matchResult

  match.__doc__ = fn.__doc__
  return match

#===============================================================================

class Pattern(object):

  NAMED = 1  # Debug only named

  #-----------------------------------------------------------------------------

  def __init__(self):
    self.dbg  = False
    self.name = None
    pass

  #-----------------------------------------------------------------------------

  def debug(self, TF=None):
    if TF is None: return self.dbg
    if isinstance(TF, basestring) and TF.lower() == "named":
      self.dbg = Pattern.NAMED
    else:
      self.dbg = TF

  #-----------------------------------------------------------------------------

  def setName(self, name):
    self.name = name

  #-----------------------------------------------------------------------------

  def match(self, string, index=0):
    """
    Implement this is child classes
    """
    return False

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

  def __ror__(self, name):
    """
    """
    return self.__or__(name)

  #-----------------------------------------------------------------------------

  def __or__(self, name):
    """
    Add a name to a pattern
    """
    if isinstance(name, bool) or name == Pattern.NAMED:
      self.debug(name)
    else:
      self.setName(name)
    return self

  #-----------------------------------------------------------------------------

  def __mul__(self, other):
    """
    Suport 'ptn*a'
    """
    return PatternAnd(self, other)

  #-----------------------------------------------------------------------------

  def __rmul__(self, other):
    """
    Support 'a*ptn'
    """
    return PatternAnd(other, self)

  #-----------------------------------------------------------------------------

  def __add__(self, other):
    """
    Support 'ptn+a'
    """
    return PatternOr(self, other)

  #-----------------------------------------------------------------------------

  def __radd__(self, other):
    """
    Support 'a+ptn'
    """
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

  def __pow__(self, n):
    """
    Support ptn**n to get at least n repeats of pattern.
    """
    return PatternRepeat(self, n)

  #-----------------------------------------------------------------------------

  def __invert__(self):
    """
    Support ~ptn as a look ahead pattern that consumes no values
    """
    if isinstance(self, PaternLookAhead): return self
    return PaternLookAhead(self)

  #-----------------------------------------------------------------------------

  def __call__(self, string, index=0):
    return self.match(string, index)

#===============================================================================

def escapeStr(string):
  for c,v in [("\r",r"\r"),("\n",r"\n"),("\t",r"\t")]:
    string = string.replace(c, v)
  return string

#===============================================================================

class P(Pattern):
  """
  Match a string or a number of characters.
  """

  #-----------------------------------------------------------------------------

  def __init__(self, value):
    Pattern.__init__(self)
    self.isValidValue(value)

    if isinstance(value, Pattern):
      self.matcher = self.match_ptn
      self.ptn     = value
      self.repr    = "P(ptn)"

    elif isinstance(value, basestring):
      self.matcher = self.match_str
      self.string  = value
      self.size    = len(value)
      # TODO: Handle signle quotes in representation.
      self.repr    = "P('%s')" % escapeStr(value)

    elif isinstance(value, bool):
      self.matcher = self.match_TF
      self.TF      = value
      self.repr    = "P(%s)" % value

    elif isinstance(value, int):
      if value >= 0:
        self.matcher = self.match_n
        self.n       = value
      else:
        self.matcher = self.match_neg
        self.n       = -value
      self.repr      = "P(%s)" % value

    elif callable(value):
      self.matcher = self.match_fn
      self.fn      = value
      self.repr    = "P(fn)"

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

  @ConfigBackCaptureString4match
  def match(self, string, index=0):
    """
    Match the given pattern
    """
    return self.matcher(string, index)

  #-----------------------------------------------------------------------------

  def match_ptn(self, string, index=0):
    """
    Matches the pattern passed in.

    >>> p = P(P("ab"))
    >>> p("abba")
    ab
    >>> p("abba",1) is None
    True
    """
    return self.ptn(string, index)

  #-----------------------------------------------------------------------------

  def match_str(self, string, index=0):
    """
    Matches an exact string.

    >>> p = P("test")
    >>> p("testing")
    test
    >>> p("A test",2)
    test
    >>> p("Failed") is None
    True
    """
    if len(string) - index < self.size: return None
    if string[index:index+self.size] == self.string:
        return Match(string, index, index + self.size)
    return None

  #-----------------------------------------------------------------------------

  def match_n(self, string, index=0):
    """
    Matches exactly n characters.

    >>> p = P(1)
    >>> p("") is None
    True
    >>> p("a")
    a
    >>> p = P(3)
    >>> p("ab") is None
    True
    >>> p("abc")
    abc
    >>> p("abc",1) is None
    True
    """
    if len(string) - index < self.n: return None
    return Match(string, index, index + self.n)

  #-----------------------------------------------------------------------------

  def match_neg(self, string, index=0):
    """
    Matches less than n characters only (end of string).

    >>> p = P(-3)
    >>> p("") == ""
    True
    >>> p("ab")
    ab
    >>> p("abc") is None
    True
    """
    sz = len(string)
    if sz - index >= self.n: return None
    return Match(string, index, sz)

  #-----------------------------------------------------------------------------

  def match_TF(self, string, index=0):
    """
    Return False if the value is False, or the 'index' value if not past end of
    string.

    >>> p = P(False)
    >>> p("test") is None
    True
    >>> p = P(True)
    >>> p("test") == ""
    True
    >>> p("test",3) == ""
    True
    >>> p("test",5) is None
    True
    """
    if not self.TF or index > len(string): return None
    return Match(string, index, index)

  #-----------------------------------------------------------------------------

  def match_fn(self, string, index=0):
    """
    Call the function with the string and the index value. If the function returns
    an integer between the index value and the length of the string, return this
    value. If the function returns True, return index. Otherwise, return False.

    >>> p = P(lambda str, i: i+2)
    >>> p("test")
    te
    >>> p("test",3) is None
    True
    >>> p = P(lambda str, i: True)
    >>> p("test",4) == ""
    True
    """
    match = self.fn(string, index)
    if match is True: return Match(string, index, index)
    if match is False: return None
    if isinstance(match, Match): return match

    if isinstance(match, int):
        if index <= match and match <= len(string):
            return Match(string, index, match)
    return None

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
    Pattern.__init__(self)
    if not isinstance(set, basestring):
      raise ValueError("The arg must be a string in S(arg)")
    self.set = set

  #-----------------------------------------------------------------------------

  @ConfigBackCaptureString4match
  def match(self, string, index=0):
    """
    Match character in the given set.

    >>> p = S("ace")
    >>> p("a")
    a
    >>> p("b") is None
    True
    >>> p("abc",2)
    c
    """
    if len(string) - index < 1: return None
    if string[index] not in self.set: return None
    return Match(string, index, index + 1)

  #-----------------------------------------------------------------------------

  def __repr__(self):
    # TODO: Handle single quote in set
    return "S('%s')" % escapeStr(self.set)

#===============================================================================

class R(Pattern):
  """
  Match characters in a given range.
  """

  #-----------------------------------------------------------------------------

  def __init__(self, *ranges):
    Pattern.__init__(self)
    self.ranges = ranges
    for range in ranges:
      if len(range) != 2: raise ValueError("Ranges must have two values: %s" % value)
      if range[0] > range[1]: raise ValueError("Lower range value must be less than upper range value: %s" % value)

  #-----------------------------------------------------------------------------

  @ConfigBackCaptureString4match
  def match(self, string, index=0):
    """
    Matches any character in the given set of ranges.

    >>> p = R("AZ","az")
    >>> p("a")
    a
    >>> p("Q")
    Q
    >>> p("1") is None
    True
    """
    if len(string) - index < 1: return False

    chr = string[index]
    for range in self.ranges:
      if range[0] <= chr and chr <= range[1]:
          return Match(string, index, index+1)
    return None

  #-----------------------------------------------------------------------------

  def __repr__(self):
    # TODO: Handle single quote in range values
    return "R(%s)" % (",".join(["'%s'" % range for range in self.ranges]))

#===============================================================================

class V(Pattern):

  #-----------------------------------------------------------------------------

  def __init__(self, var=None):
    Pattern.__init__(self)
    self.var = var

  #-----------------------------------------------------------------------------

  def setPattern(self, pattern):
    if not isinstance(pattern, Pattern):
      raise ValueError("The setPattern method of V class needs to be passed a Pattern object.")
    self.pattern = pattern

  #-----------------------------------------------------------------------------

  @ConfigBackCaptureString4match
  def match(self, string, index=0):
    """
    """
    return self.pattern.match(string, index)

  #-----------------------------------------------------------------------------

  def __repr__(self):
    return "V(%s)" % self.var if self.var else "V(%s)" % repr(self.pattern)

#===============================================================================
# Captures
#===============================================================================

class C(Pattern):
  """
  Capture a pattern
  """

  #-----------------------------------------------------------------------------

  def __init__(self, pattern):
    Pattern.__init__(self)
    self.pattern = pattern

  #-----------------------------------------------------------------------------

  @ConfigBackCaptureString4match
  def match(self, string, index=0):
    """
    >>> p = C(C(P(2))*P(1))
    >>> match = p("abcd")
    >>> match.getCapture(0)
    'abc'
    >>> match.getCapture(1)
    'ab'
    """

    match = self.pattern.match(string, index)
    if isinstance(match, Match):
      match.captures.insert(0, str(match))
    return match

  #-----------------------------------------------------------------------------

  def __repr__(self):
    return "C(%s)" % repr(self.pattern)

#===============================================================================

class Cb(Pattern):
  """
  Backcapture
  """

  #-----------------------------------------------------------------------------

  def __init__(self, name, pattern=None):
    Pattern.__init__(self)
    self.capname = name
    self.pattern = pattern

  #-----------------------------------------------------------------------------

  @ConfigBackCaptureString4match
  def match(self, string, index=0):
    """
    >>> p = Cb("test",P("cat")+P("dog")) * P(" ") * Cb("test")
    >>> p.match("dog dog")
    dog dog
    >>> p.match("cat cat")
    cat cat
    >>> p.match("cat dog") == None
    True
    """
    if self.pattern is None:
      tomatch = string.getNamedCapture(self.capname)
      return P(tomatch).match(string, index)
    else:
      match = self.pattern.match(string, index)
      if isinstance(match, Match):
        string.addNamedCapture(self.capname, match.getValue())
    return match

  #-----------------------------------------------------------------------------

  def __repr__(self):
    # TODO: handle single quote in name
    if self.pattern is None:
      return "Cb('{0}')".format(self.capname)
    return "Cb('{0}',{0})".format(self.capname, repr(self.pattern))

#===============================================================================

class Cc(Pattern):
  """
  Capture a constant value.
  """

  #-----------------------------------------------------------------------------

  def __init__(self, value):
    Pattern.__init__(self)
    self.value = value

  #-----------------------------------------------------------------------------

  @ConfigBackCaptureString4match
  def match(self, string, index=0):
    """

    >>> p = Cc("test")
    >>> match = p("")
    >>> match[0]
    'test'
    """
    return Match(string, index, index).addCapture(self.value)

  #-----------------------------------------------------------------------------

  def __repr__(self):
    return "Cc(%s)" % self.value

#===============================================================================

class Cg(Pattern):

  #-----------------------------------------------------------------------------

  def __init__(self, pattern, dropIfEmpty=True):
    Pattern.__init__(self)
    self.pattern     = pattern
    self.dropIfEmpty = dropIfEmpty

  #-----------------------------------------------------------------------------

  @ConfigBackCaptureString4match
  def match(self, string, index=0):
    """
    >>> p = Cg(C(P(1)) * C(P(1)))
    >>> p("Test").getCapture(0)
    ['T', 'e']
    >>> p("b") is None
    True
    """

    match = self.pattern.match(string, index)
    if not isinstance(match, Match): return match

    captures = match.captures
    if len(captures) == 0 and self.dropIfEmpty: return match

    # Make the captures a single entry in the captures array
    match.captures = [captures]
    return match

  #-----------------------------------------------------------------------------

  def __repr__(self):
    if self.dropIfEmpty is False:
      return "Cg({0},{1})".format(repr(self.pattern),"False")
    return "Cg({0})".format(repr(self.pattern))

#===============================================================================

class Cp(Pattern):

  #-----------------------------------------------------------------------------

  def __init__(self):
    Pattern.__init__(self)

  #-----------------------------------------------------------------------------

  @ConfigBackCaptureString4match
  def match(self, string, index=0):
    """
    >>> p = Cp()
    >>> p("test",3).getCapture(0)
    3
    """
    if index < 0 or len(string) < index: return None
    return Match(string, index, index).addCapture(index)

  #-----------------------------------------------------------------------------

  def __repr__(self):
    return "Cp()"

#===============================================================================
# Pattern Operators
#===============================================================================

class PatternAnd(Pattern):
  """
  Look for the first pattern in the list that matches the string.
  """

  #-----------------------------------------------------------------------------

  def __init__(self, pattern1, pattern2):
    Pattern.__init__(self)
    if not isinstance(pattern1, Pattern) and not isinstance(pattern2, Pattern):
      raise ValueError("PatternAnd requires the first or second constructor item to be a Pattern")

    isValidValue = P.isValidValue
    isValidValue(pattern1, msg="For 'a*b', 'a' must be Pattern or int value")
    isValidValue(pattern2, msg="For 'a*b', 'b' must be Pattern or int value")

    asPattern = P.asPattern
    self.patterns = [asPattern(pattern1), asPattern(pattern2)]

  #-----------------------------------------------------------------------------

  @ConfigBackCaptureString4match
  def match(self, string, index=0):
    """
    Find the first pattern that matches the string.

    >>> p = P("bob ") * P("bill ") * P("fred")
    >>> p("bob bill fred")
    bob bill fred
    >>> p("bob bill fran") is None
    True
    >>> p = P("tes") - P("test")
    >>> p("tesseract")
    tes
    >>> p("testing") is None
    True
    """

    MATCH = Match(string, index)
    # Make sure all the patterns match
    for pattern in self.patterns:
      match = pattern.match(string, index)
      if not isinstance(match, Match): return None
      MATCH.addSubmatch(match)
      index = match.end
    MATCH.end = index
    return MATCH

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
    Pattern.__init__(self)
    if not isinstance(pattern1, Pattern) and not isinstance(pattern2, Pattern):
      raise ValueError("PatternOr requires the first or second constructor item to be a Pattern")

    isValidValue = P.isValidValue
    isValidValue(pattern1, msg="For 'a+b', 'a' must be Pattern or int value")
    isValidValue(pattern2, msg="For 'a+b', 'b' must be Pattern or int value")

    asPattern = P.asPattern
    self.patterns = [asPattern(pattern1), asPattern(pattern2)]

  #-----------------------------------------------------------------------------

  @ConfigBackCaptureString4match
  def match(self, string, index=0):
    """
    Find the first pattern that matches the string.

    >>> p = P("bob") + P("bill") + P("fred")
    >>> p("obob",1)
    bob
    >>> p("duck bill",5)
    bill
    >>> p("fred")
    fred
    >>> p("none") is None
    True
    """

    for pattern in self.patterns:
      match = pattern.match(string, index)
      if isinstance(match, Match): return match
    return None

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
    Pattern.__init__(self)
    P.isValidValue(pattern, msg ="Invalid '-ptn' expression")
    self.pattern = P.asPattern(pattern)

  #-----------------------------------------------------------------------------

  @ConfigBackCaptureString4match
  def match(self, string, index=0):
    """

    >>> p = -P("bob")
    >>> p("bob") is None
    True
    >>> p("fred") == ""
    True
    """

    match = self.pattern(string, index)
    if not isinstance(match, Match): return Match(string, index, index)
    return None

  #-----------------------------------------------------------------------------

  def __repr__(self):
    return "-%s" % repr(self.pattern)

#===============================================================================

class PatternRepeat(Pattern):

  #-----------------------------------------------------------------------------

  def __init__(self, pattern, n):
    Pattern.__init__(self)
    if not isinstance(pattern, Pattern): raise ValueError("First value to PatternRepeat must be a pattern")
    if not isinstance(n, int): raise ValueError("In ptn^n, n must be an integer value")
    self.pattern = pattern

    if n >= 0:
      self.matcher = self.match_at_least_n
      self.n = n
    else:
      self.matcher = self.match_at_most_n
      self.n = -n

  #-----------------------------------------------------------------------------

  @ConfigBackCaptureString4match
  def match(self, string, index=0):
    return self.matcher(string, index)

  #-----------------------------------------------------------------------------

  def match_at_least_n(self, string, index=0):
    """

    >>> p = S("abc")**3
    >>> p("ab") is None
    True
    >>> p("abc")
    abc
    >>> p("abcabcd")
    abcabc
    """
    MATCH = Match(string, index)
    cnt = 0
    while True:
      match = self.pattern.match(string, index)

      if not isinstance(match, Match):
        return MATCH.setEnd(index) if cnt >= self.n else None

      MATCH.addSubmatch(match)

      # No progress, so it matches infinite times
      if match.end == index: return MATCH.setEnd(index)

      cnt += 1
      index = match.end

  #-----------------------------------------------------------------------------

  def match_at_most_n(self, string, index=0):
    """

    >>> p = S("abc")**-3
    >>> p("") == ""
    True
    >>> p("abca")
    abc
    """
    MATCH = Match(string, index)
    for i in range(self.n):
      match = self.pattern.match(string, index)
      if not isinstance(match, Match): return MATCH.setEnd(index)
      MATCH.addSubmatch(match)
      index = match.end
    return MATCH.setEnd(index)

  #-----------------------------------------------------------------------------

  def __repr__(self):
    return "%s**%s" % (repr(self.pattern), self.n)

#===============================================================================

class PaternLookAhead(Pattern):
  """
  Check whether the patern matches the string that follows without consuming the
  string
  """

  #-----------------------------------------------------------------------------

  def __init__(self, pattern):
    Pattern.__init__(self)
    P.isValidValue(pattern)
    self.pattern = P.asPattern(pattern)

  #-----------------------------------------------------------------------------

  @ConfigBackCaptureString4match
  def match(self, string, index=0):
    """

    >>> p = ~P("test")
    >>> p("testing") == ""
    True
    >>> p("This is a test",10) == ""
    True
    >>> p("Failed") is None
    True
    """
    match = self.pattern.match(string, index)
    if isinstance(match, Match): return match.setEnd(index)
    return None

  #-----------------------------------------------------------------------------

  def __repr__(self):
    return "~%s" % repr(self.pattern)

#===============================================================================
# BackCaptureString
#===============================================================================

class BackCaptureString(object):
  """
  This class is used to track the string that is being matched against and any
  back captures that are generated. Back captures are stored in a stack. Back
  captures that are added as part of a pattern that fails are removed from the
  stack.
  """

  #-----------------------------------------------------------------------------

  def __init__(self, string):
    self.string = string
    self.backcaptures = []
    self.dbg = False

  #-----------------------------------------------------------------------------

  def debug(self, TF=None):
    if TF is None: return self.dbg
    self.dbg = TF

  #-----------------------------------------------------------------------------

  def addNamedCapture(self, name, capture):
    """
    Add a named capture to the list of back captures.
    """
    self.backcaptures.append((name, capture))

  #-----------------------------------------------------------------------------

  def getNamedCapture(self, name):
    """
    Get a named capture from the list. The most recent capture of the given
    name is returned.
    """

    for i in xrange(self.getStackSize()-1,-1,-1):
      bcname, capture = self.backcaptures[i]
      if bcname == name: return capture

    raise IndexError("No backcapture was found for '{0}'".format(name))

  #-----------------------------------------------------------------------------

  def getStackSize(self):
    """
    Get the number of back captures
    """
    return len(self.backcaptures)

  #-----------------------------------------------------------------------------

  def setStackSize(self, size):
    """
    Set the stack back to the given size. If the stack is too large raise an
    Exception.
    """
    sz = len(self.backcaptures)
    if size == sz: return
    if sz < size: raise ValueError("The backcaptures stack is too short.")

    self.backcaptures = self.backcaptures[0:size]

  #-----------------------------------------------------------------------------

  def __getitem__(self, index):
    if isinstance(index, (int,slice)):
      return self.string[index]

    return self.backcaptures[index]

  #-----------------------------------------------------------------------------

  def __len__(self):
    return len(self.string)

  #-----------------------------------------------------------------------------

  def __repr__(self):
    return self.string

#===============================================================================
# Match object
#===============================================================================

class Match(object):

  #-----------------------------------------------------------------------------

  def __init__(self, string, start, end=None):
    self.string   = string
    self.start    = start
    self.end      = end
    self.captures = []

  #-----------------------------------------------------------------------------

  def setEnd(self, end):
    """
    Set the value of end and return the match
    """
    self.end = end
    return self

  #-----------------------------------------------------------------------------

  def getValue(self, default=None):
    """
    Get the value that was mached.
    """
    start, end = (self.start, self.end)
    return default if self.end is None else self.string[start:end]

  #-----------------------------------------------------------------------------

  def addCapture(self, capture):
    """
    Add a capture or a submatch.
    """
    self.captures.append( capture )
    return self

  #-----------------------------------------------------------------------------

  def addSubmatch(self, match):
    """
    """
    self.captures.extend(match.captures)
    return self

  #-----------------------------------------------------------------------------

  def hasCaptures(self):
    return len(self.captures) > 0

  #-----------------------------------------------------------------------------

  def getCapture(self, index):
    """
    """
    if not self.hasCaptures() or index >= len(self.captures):
      raise IndexError("Invalid capture index for Match")
    return self.captures[index]

  #-----------------------------------------------------------------------------

  def __getitem__(self, key):
    """
    Get a capture from the Match object
    """
    if isinstance(key, int) and 0 <= key and key < len(self):
      return self.getCapture(key)
    raise IndexError("Invalid index for Match")

  #-----------------------------------------------------------------------------

  def __eq__(self, other):
    """
    Compare with strings or other Match objects. Check that the resulting value
    matches.
    """
    if isinstance(other, basestring):
      return str(self) == other

    if isinstance(other, Match):
      return str(self) == str(other)

  #-----------------------------------------------------------------------------

  def __len__(self):
    return len(self.captures)

  #-----------------------------------------------------------------------------

  def __repr__(self):
    return str(self)

  #-----------------------------------------------------------------------------

  def __str__(self):
    return self.getValue()

#===============================================================================

def match(pattern, subject, index=0):
  """
  """
  pass

#===============================================================================

def Token(object):

  #-----------------------------------------------------------------------------

  def __init__(self, name, match):
    self.name = name
    self.match = match

#===============================================================================

class Tokenizer(object):

  #-----------------------------------------------------------------------------

  def __init__(self, *tokens):
    self.tokens = []
    for token in tokens:
      self.addToken(token)

  #-----------------------------------------------------------------------------

  def addToken(self, pattern):
    if pattern.name is None:
      raise ValueError("A token must be a named pattern")
    self.tokens.append( pattern )

  #-----------------------------------------------------------------------------

  def getTokens(self, string, index=0):
    """
    """

    while True:
      for pattern in self.tokens:
        name = pattern.name
        match = pattern.match(string, index)
        if isinstance(match, Match):
          yield (name, match)
          if index == match.end: raise StopIteration() # No Progress
          index = match.end
          break
      else:
        raise StopIteration()


#===============================================================================

if __name__ == "__main__":
  import doctest
  doctest.testmod()

