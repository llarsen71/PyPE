#===============================================================================

class Pattern(object):

  def __init__(self):
    pass

  #-----------------------------------------------------------------------------

  def match(self, string, init=0):
    pass

  #-----------------------------------------------------------------------------

  def __xor__(self, n):
    """
    Support ptn^n to get at least n repeats of pattern.
    """
    return PatternRepeat(self, n)

  #-----------------------------------------------------------------------------

  def __call__(self, string, init=0):
    return self.match(string, init)

#===============================================================================

class PatternRepeat(Pattern):
  def __init__(self, pattern, n):
    if not issubclass(pattern.__class__, Pattern): raise ValueError("First value to PatternRepeat must be a pattern")
    if not isinstance(n, int): raise ValueError("In ptn^n, n must be an integer value")
    self.pattern = pattern

    if n >= 0:
      self.match = self.match_at_least_n
      self.n = n
    else:
      self.match = self.match_at_most_n
      self.n = -n

  #-----------------------------------------------------------------------------

  def match_at_least_n(self, string, init=0):
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
      init1 = self.pattern.match(string, init)

      # No progress, so it matches infinite times
      if init == init1: return init
      if init1 == False or init > init1 or init1 > len(string):
        if cnt >= self.n: return init
        return False

      cnt += 1
      init = init1

  #-----------------------------------------------------------------------------

  def match_at_most_n(self, string, init=0):
    """

    >>> p = S("abc")^-3
    >>> p("")
    0
    >>> p("abca")
    3
    """

    init1 = init
    for i in range(self.n):
      init1 = self.pattern.match(string, init)
      if init1 == False: return init
      init = init1
    return init1

#===============================================================================

class P(Pattern):

  def __init__(self, value):
    if isinstance(value, basestring):
      self.match  = self.match_str
      self.string = value
      self.size   = len(value)

    elif isinstance(value, bool):
      self.match  = self.match_TF
      self.TF     = value

    elif isinstance(value, int):
      if value >= 0:
        self.match  = self.match_n
        self.n      = value
      else:
        self.match  = self.match_neg
        self.n      = -value

    elif callable(value):
      self.match  = self.match_fn
      self.fn     = value

  #-----------------------------------------------------------------------------

  def match_str(self, string, init=0):
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
    if len(string) - init < self.size: return False
    if string[init:init+self.size] == self.string: return init + self.size
    return False

  #-----------------------------------------------------------------------------

  def match_n(self, string, init=0):
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
    if len(string) - init < self.n: return False
    return init + self.n

  #-----------------------------------------------------------------------------

  def match_neg(self, string, init=0):
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
    if sz - init >= self.n: return False
    return sz

  #-----------------------------------------------------------------------------

  def match_TF(self, string, init=0):
    """
    Return False if the value is False, or the 'init' value if not past end of
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
    if not self.TF or init > len(string): return False
    return init

  #-----------------------------------------------------------------------------

  def match_fn(self, string, init=0):
    """
    Call the function with the string and the init value. If the function returns
    an integer between the init value and the length of the string, return this
    value. If the function returns True, return init. Otherwise, return False.

    >>> p = P(lambda str, i: i+2)
    >>> p("test")
    2
    >>> p("test",3)
    False
    >>> p = P(lambda str, i: True)
    >>> p("test",4)
    4
    """
    result = self.fn(string, init)
    if init <= result and result <= len(string): return result
    if result == True: return init
    return False

#===============================================================================

class S(Pattern):
  """
  Match any of a given set of characters.
  """

  def __init__(self, set):
    self.set = set

  #-----------------------------------------------------------------------------

  def match(self, string, init=0):
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
    if len(string) - init < 1: return False
    if string[init] not in self.set: return False
    return init + 1

#===============================================================================

class R(Pattern):
  """
  Match characters in a given range.
  """

  def __init__(self, *ranges):
    self.ranges = ranges
    for range in ranges:
      if len(range) != 2: raise ValueError("Ranges must have two values: %s" % value)
      if range[0] > range[1]: raise ValueError("Lower range value must be less than upper range value: %s" % value)

  #-----------------------------------------------------------------------------

  def match(self, string, init=0):
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
    if len(string) - init < 1: return False

    chr = string[init]
    for range in self.ranges:
      if range[0] <= chr and chr <= range[1]: return init+1
    return False

#===============================================================================

def match(pattern, subject, init=0):
  """
  """
  pass

#===============================================================================

if __name__ == "__main__":
  import doctest

  doctest.testmod()