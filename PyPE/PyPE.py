# ==============================================================================

class Stack(object):
  """
  This implements a stack that wraps a parent stack. Changes to the parent
  Stack are only made permanent (i.e., comitted to the parent Stack) when
  'commit' is called.

  This is used for Stack based captures for grammars that require context.
  """

  # ----------------------------------------------------------------------------

  def __init__(self, parent = None):
    """
    :param parent: The parent Stack to push changes to when changes are committed.
    """
    self.parent = parent
    self.parent_pop = 0   # Record how many values have been popped from the parent.
    self.stack = []

  # ----------------------------------------------------------------------------

  def __parentlen__(self):
    """
    Get the virtual length of the parent stack (i.e., the length minus the number
    of items popped from the parent Stack). Note that items popped from the
    parent Stack are not actually removed from the Stack until 'commit' is
    called.
    """
    if not self.hasParent(): return 0
    return len(self.parent) - self.parent_pop

  # ----------------------------------------------------------------------------

  def __contains__(self, value):
    """
    Check whether the stack contains a value
    :param value: The value to look for
    :return: True if the value is in the stack. Otherwise False.
    """
    return value in self.stack or (self.hasParent() and value in self.parent)

  # ----------------------------------------------------------------------------

  def __len__(self):
    """
    Get the length of the stack. This includes the length inherited from the
    parent stack.
    :return: The length of the stack.
    """
    return self.__parentlen__() + len(self.stack)

  # ----------------------------------------------------------------------------

  def __getitem__(self, idx):
    """
    Get an item or range of items from the Stack.
    :param idx: Index of the item from the Stack to retrieve or a slice to get a
                range of times. Positive or negative indexes as with standard
                python arrays.
    :return: The requested item(s).
    """
    if isinstance(idx, slice):
      index = lambda i, default: default if i is None else len(self)+i if i < 0 else i
      start = index(idx.start, 0)
      stop  = index(idx.stop,  len(self))
      step  = index(idx.step,  1)
      return [self[i] for i in range(start, stop, step)]

    if not isinstance(idx, int): raise IndexError("Invalid stack index type")

    # Handle negative index values
    idx = self._adjustIndex(idx)
    if not self.isValidIndex(idx): raise IndexError("Invalid stack index {0}".format(idx))

    parentlen = self.__parentlen__()
    if idx < parentlen: return self.parent[idx]
    idx = idx - parentlen
    return self.stack[idx]

  # ----------------------------------------------------------------------------

  def _adjustIndex(self, idx):
    """
    Convert negative index to a valid positive index if possible.

    :param idx: The index to adjust
    :return: A valid positive index or the original index
    """
    if idx >= 0: return idx

    # Try to convert this to a positive index.
    idx2 = len(self) + idx
    return idx if idx2 < 0 else idx2

  # ----------------------------------------------------------------------------

  def isValidIndex(self, idx):
    """
    Check whether the given index is a valid stack index.

    :param idx: The index to check
    :return: True if the index is value, otherwise False.
    """
    idx = self._adjustIndex(idx)
    return 0 <= idx and idx < len(self)

  # ----------------------------------------------------------------------------

  def append(self, value):
    """
    Append a value to the Stack.
    :param value: The value to add to the Stack
    :return: The Stack object
    """
    self.stack.append(value)
    return self

  # ----------------------------------------------------------------------------

  def extend(self, values):
    """
    Extend the Stack with a set of values
    :param values: The list of values to add to the Stack
    :return: The Stack object
    """
    self.stack.extend(values)
    return self

  # ----------------------------------------------------------------------------

  def pop(self, n=None):
    """
    Pop(remove) one or more items from the stack and return them.

    :param n: The number of items from the stack to pop. 'all' for all items on stack.
    :return: The items popped from the stack.
    """
    if isinstance(n, int):
      if n <= 0: return []
      items = [self.pop() for i in xrange(n)]
      items.reverse()
      return items

    if n == "all":
      return self.pop(len(self))

    item = self.peek()
    if len(self.stack) > 0: self.stack.pop()
    elif self.__parentlen__() > 0: self.parent_pop += 1
    return item

  # ----------------------------------------------------------------------------

  def peek(self):
    """
    View the last item added to the stack
    :return: The last item added to the stack
    """
    if len(self.stack) > 0: return self.stack[-1]
    parentlen = self.__parentlen__()
    if parentlen == 0: return None
    return self.parent[parentlen-1]

  # ----------------------------------------------------------------------------

  def hasParent(self):
    """
    Check whether a parent is specified for this stack object.
    :return: Boolean indicating whether this Stack object has a parent.
    """
    return self.parent is not None

  # ----------------------------------------------------------------------------

  def commit(self):
    """
    Commit the changes to the parent stack. Clear all changes from this Stack.
    Note that this may pop items from the parent Stack if more items have
    been popped than are on the current Stack.

    :return: The parent Stack
    """
    if not self.hasParent(): return

    for i in range(self.parent_pop): self.parent.pop()
    self.parent.extend(self.stack)

    # Reset the stack and
    self.stack = []
    self.parent_pop = 0
    return self.parent

  # ----------------------------------------------------------------------------

  def __str__(self):
    return str([item for item in self])

# ==============================================================================

class Context(object):
  """
  Store context for a match. This includes any Stacks used by the match routine.
  """

  # ----------------------------------------------------------------------------

  def __init__(self, parent = None):
    self.parent = parent
    self.stacks = {}
    self.debug = parent.debug if parent is not None else None

  # ----------------------------------------------------------------------------

  def __contains__(self, stack):
    return stack in self.stacks or (self.hasParent() and stack in self.parent)

  # ----------------------------------------------------------------------------

  def __getitem__(self, stack):
    if stack in self.stacks: return self.stacks[stack]
    if self.hasParent() and stack in self.parent: return self.parent[stack]
    raise IndexError("Requested stack not found ({0})".format(stack))

  # ----------------------------------------------------------------------------

  def hasParent(self):
    """
    Check whether a parent is specified for this stack object.

    :return: Boolean indicating whether this Stack object has a parent.
    """
    return self.parent is not None

  # ----------------------------------------------------------------------------

  def getStack(self, stack, wrapStack=False):
    """
    Get the requested stack.

    :param stack: The name of the stack.
    :param wrapStack: If the stack is only in the parent object, create a new
           stack wrapper in this object if wrapStack is True.
    :return: The stack object.
    """
    if stack in self.stacks: return self.stacks[stack]
    if wrapStack:
      thestack = Stack(self.parent[stack]) if self.hasParent() and stack in self.parent else Stack()
      self.stacks[stack] = thestack
      return thestack
    if self.hasParent() and stack in self.parent: return self.parent[stack]
    return None

  # ----------------------------------------------------------------------------

  def append(self, stack, value):
    """
    Append the given value to the stack.

    :param stack: The stack to append to
    :param values: The value to append
    :return: The Context object
    """
    thestack = self.getStack(stack, wrapStack=True)
    thestack.append(value)
    return self

  # ----------------------------------------------------------------------------

  def extend(self, stack, values):
    """
    Extend the stack with the given values.

    :param stack: The stack to append to
    :param values: A list of values to append
    :return: The Context object
    """
    if len(values) == 0: return
    thestack = self.getStack(stack, wrapStack=True)
    thestack.extend(values)
    return self

  # ----------------------------------------------------------------------------

  def peek(self, stack):
    """
    Return the last value added to the stack without removing it.

    :param stack: The stack to peek at.
    :return: The last value added to the stack.
    """
    thestack = self[stack]
    return thestack.peek() if thestack is not None else None

  # ----------------------------------------------------------------------------

  def pop(self, stack, n = None):
    """
    Pop the last value added to the stack off the stack and return it.

    :param stack: The stack to work with.
    :param n: The number of items to pop from the stack. 'all' for all items.
    :return: The last value added to the stack.
    """
    thestack = self.getStack(stack, wrapStack=True)
    return thestack.pop(n)

  # ----------------------------------------------------------------------------

  def commit(self):
    """
    Commit the changes in the context to the parent context.

    :return: The parent Context
    """
    if not self.hasParent(): return

    # Commit all of the stacks from the current Context to the parent
    for stack, thestack in self.stacks.items():
      if not thestack.hasParent():
        if stack in self.parent:
          raise IndexError("The current Context is out of sync with its parent Context - unconnected stack {0}".format(stack))
        self.parent.stacks[stack] = thestack
        continue
      thestack.commit()

    # Clear the stacks since they are committed.
    self.stacks = {}
    return self.parent

# ==============================================================================

def ConfigBackCaptureString4match(fn):
  """
  This decorates the :func:`match` functions in the Pattern subclasses. The
  wrapper function does the following:

  * It wraps the string that is passed to pattern's *match* function as a
    :class:`BackCaptureString` so that back captures are stored correctly.
  * The debug option for a pattern is forwarded to any contained patterns via
    the wrapper function.
  * The *match* function for the pattern is called.
  * Debug messages are printed if when debugging is active for a pattern.
  * The function cleans up back captures that are out of scope.
  * Results from the *match*

  :param fn: A :func:`match` function that takes a string and and optional index
             and returns a :class:`Match` object if the string matches the
             pattern, or None if the pattern fails.
  :type fn: function(string[, index=0])

  :returns: The wrapper function that performs the tasks outlined above.
  """

  def match(pattern, string, index=0, context=None):
    if not isinstance(string, BackCaptureString): string = BackCaptureString(string)
    sz = string.getStackSize()

    # Get the currently active debug options
    debug = context.debug if context is not None else None

    # Wrap the context
    context = Context(context)

    # If the current pattern has a debug object (other than None), store the
    # value in the context to forward to other patterns.
    if pattern.debug() is not None:
      debug = context.debug = pattern.debug()

    # Convert negative index to positive index
    index = pattern._positiveIndex(string, index)

    if debug: debug.beforeMatch(pattern, string, index, context)

    # Get the match result and add the context to it.
    matchResult = fn(pattern, string, index, context)
    matchSucceeded = isinstance(matchResult, Match)
    if matchSucceeded:
      matchResult.context = context

    if debug: debug.afterMatch(pattern, string, index, context, matchResult)

    # Clear any nested stored callback items except when:
    #
    # 1. We return from a Cb item that stores a callback.
    # 2. We are in a sequence of 'PatternAnd' matches. These should be
    #    considered to be at the same level in the PEG logic, so we keep any
    #    previous captured callbacks in the sequence. Once the combined sequence
    #    of PatternAnd(s) returns, the callbacks are removed. The 'is_sub_and'
    #    flag indicates whether a PatternAnd object is contained within another
    #    PatternAnd (i.e., is part of a sequence).

    if not isinstance(pattern, Cb) and not (isinstance(pattern, PatternAnd) and pattern.is_sub_and):
      string.setStackSize(sz)

    # Pass context result to the parent context.
    if matchSucceeded: context.commit()

    return matchResult

  # Preserve the doc string for the original match function
  match.__doc__ = fn.__doc__
  return match

# ==============================================================================

def escapeStr(string):
  """
  Convert \r, \n, and \t to text representations and replace quote marks with
  \' and \".

  :param string: The string to modify
  :return: The escaped string.
  """
  for c, v in [("\r",r"\r"),("\n",r"\n"),("\t",r"\t"),("'",r"\'"),('"',r'\"')]:
               #("\\",r"\\")]:
    string = string.replace(c, v)
  return string

# ==============================================================================

def ANDfilter(first, second):
  def AND(**args):
    return first(**args) and second(**args)
  return AND

# ==============================================================================

def ORfilter(first, second):
  def OR(**args):
    return first(**args) or second(**args)
  return OR

# ==============================================================================

def registerDbgFilter(filter):
  DebugOptions.registerFilter(filter)
  return filter

# ==============================================================================

class DebugOptions(object):

  # Register filters that can be used with DebugOptions class.
  filters = {}

  # ----------------------------------------------------------------------------

  @staticmethod
  def registerFilter(filter, name=None):
    """
    The beforeMatch and afterMatch function each use a filter to determine if
    debug information will be displayed.

    :param filter: A function of the form:
           `trueOrFalse = filter(**args)`
           The args are pattern, string, index, context, and possibly match
    :param name: The name to register the filter under. If no name is passed in
            the name of the function is used.`
    :return: DebugOptions object
    """

    name = name or filter.__name__
    DebugOptions.filters[name] = filter

  # ==============================================================================

  @staticmethod
  def baseFilters():
    """
    Register the Default set of filters
    """

    @registerDbgFilter
    def hide(**args): return False

    @registerDbgFilter
    def show(**args): return True

    @registerDbgFilter
    def named(pattern=None, **args): return pattern.name is not None

    @registerDbgFilter
    def show_only_success(**args): return isinstance(args['match'], Match) \
                                   if 'match' in args else True

  # ----------------------------------------------------------------------------

  @staticmethod
  def printEnter(pattern, string, index, context):
    if pattern.name is None: return
    line = string.getLineNumber(index)
    col = string.getColumnNumber(index)
    print "Enter: <{0}> => ({1}.{2}) {3}".format(pattern.name, line, col, repr(pattern))

  # ----------------------------------------------------------------------------

  @staticmethod
  def printMatch(pattern, string, index, context, match):

    line = string.getLineNumber(index)
    col = string.getColumnNumber(index)
    name = "<{0}>".format(pattern.name) if pattern.name else repr(pattern)

    print "Pattern: ({0}.{1}) {2}".format(line, col, name)
    if match is None:
      print "  Failed"
    else:
      print "  Result: '{0}'".format(escapeStr(str(match)))
      if isinstance(pattern, Capture):
        print "  Captures: {0}".format(match.captures)
      if isinstance(pattern, StackPtn):
        print "  Stack: {0} => {1}".format(pattern.stack, context.getStack(pattern.stack))

  # ----------------------------------------------------------------------------

  defaultBeforeMatchWriter = printEnter
  defaultAfterMatchWriter  = printMatch

  # ----------------------------------------------------------------------------

  @staticmethod
  def parseFilter(filter):
    """
    This takes a filter function or a filter specification string. A filter
    specification is a string that indicates a set of registered filters to
    use combined with and '&' and or '|' logic. Parenthesis can be used to
    group filter items.

    :param filter: A filter function.
    :return: The constructed filter.
    """

    if filter is None: return DebugOptions.filters['hide']
    if callable(filter): return filter

    # TODO: This logic is incomplete. No value is returned and filter is not used.
    FILTER = C((alpha + '_') * (alpha + digit + '_') ** 0)
    EXPR = 'EXPR' | Cg(
      whitespace0 * (V('PRNS') + FILTER) * whitespace0 * C(S('&|')) * \
      whitespace0 * (V('EXPR') + FILTER + V('PRNS')))
    PRNS = 'PRNS' | whitespace0 * '(' * (EXPR + FILTER + V('PRNS')) * ')'
    filterSpec = EXPR + PRNS + FILTER
    setVs(EXPR, [EXPR, PRNS])
    setVs(PRNS, [PRNS])

    # --------------------------------------------------------------------------
    def handleItem(item):
      if isinstance(item, list): return handleOp(item)
      return DebugOptions.filters[str(item)]
    # --------------------------------------------------------------------------
    def handleOp(op):
      left = handleItem(op[0])
      right = handleItem(op[2])
      if str(op[1]) == '&': return ANDfilter(left, right)
      if str(op[1]) == '|': return ORfilter(left, right)
      raise Exception("Unexpected debug filter operation")
    # --------------------------------------------------------------------------

    filter = handleItem(filterSpec.match(filter))
    return filter

  # ----------------------------------------------------------------------------

  def __init__(self, matchFilter=None,
               beforeMatchFilter=None, afterMatchFilter=None,
               beforeMatchWriter=None, afterMatchWriter=None):
    """
    Set up the filters for this DebugOptions object.

    :param matchFilter: Filter to be used before and after match. If this is
           passed in, the beforeMatchFilter and afterMatchFilter parameters are
           ignored.
    :param beforeMatchFilter: A filter spec (for parseFilter function) or filter
           function used by the `beforeMatch` event. See `registerFilter` for
           the filter function signature.
    :param afterMatchFilter:  A filter spec (for parseFilter function) or a
           filter function used by the `afterMatch` event.  See `registerFilter`
           for the filter function signature.
    :param beforeMatchWriter: The function to use to handle debug info before a
           match. Default is `printEnter` function.
    :param afterMatchWriter: The function to use to handle debug info after a
           match. Default is `printMatch`.
    """
    if matchFilter:
      self.beforeMatchFilter = self.afterMatchFilter = self.parseFilter(matchFilter)
    else:
      # Set the before and after match Filters
      self.beforeMatchFilter = self.parseFilter(beforeMatchFilter)
      self.afterMatchFilter  = self.parseFilter(afterMatchFilter)

    # Functions to write out debug information
    self.beforeMatchWriter = beforeMatchWriter or self.defaultBeforeMatchWriter
    self.afterMatchWriter  = afterMatchWriter  or self.defaultAfterMatchWriter

  # ----------------------------------------------------------------------------

  def beforeMatch(self, pattern, string, index, context):
    """
    Called before a match is performed to print debug information

    :param pattern: The pattern being matched.
    :param string: The string to match against.
    :param index: Location where match starts.
    :param context: The context that is forwarded while matching.
    """
    if self.beforeMatchFilter(pattern = pattern, string = string, index = index,
                              context = context):
      self.beforeMatchWriter(pattern = pattern, string = string, index = index,
                             context = context)

  # ----------------------------------------------------------------------------

  def afterMatch(self, pattern, string, index, context, match):
    """
    Called after a match is performed to print debug information.

    :param pattern: The pattern that was being matched.
    :param string: The string to match against
    :param index: Location where match starts
    :param context: The context that is forwarded while matching
    :param match: The pattern match (may be None)
    """

    if self.afterMatchFilter(pattern = pattern, string = string, index = index,
                             context = context, match = match):
      self.afterMatchWriter(pattern = pattern, string = string, index = index,
                            context = context, match = match)

# Set up the base filters
DebugOptions.baseFilters()

# ==============================================================================

class Pattern(object):
  """
  Abstract base class for all parsing expression patterns.
  """
  precedence = 100

  # ----------------------------------------------------------------------------

  def __init__(self):
    self.dbg  = None
    self.name = None
    pass

  # ----------------------------------------------------------------------------

  def debug(self, debugOpt=None, **args):
    """
    Set or return the debug options for this pattern. The basic options that can
    be set are:

    * True or 'show' to show parsing debug information for the current pattern
      and all contained patterns.
    * False or 'hide' to suppress debug information for the current pattern and
      all contained patterns.
    * 'named' to show parsing debug information for any named patterns contained
      within the current pattern.

    Other options may be added. For the available options, see the
    :class:`DebugOptions` class constructor which is called with the parameters
    sent to this function.

    When the debug option is set to True, pattern results are printed to the
    console by default. The output source can be modified via a custom
    :class:`DebugOptions` object.

    When the debug option is set to 'show', 'hide', or 'named', the option
    applies to any contained patterns that do not have some other other
    explicitly set.

    :param debugOpt: This option can be an object that implements the
           `beforeMatch` and `afterMatch` functions with signatures that match
           the `DebugOptions` functions of the same name. If this is True or
           'show', debugging is enabled. If this is False or 'hide', debugging
           is disabled. If this is 'named', only named patterns are shown. If
           this is 'show_only_success', only successful matches are shown. If
           this is a function, it is used as a `DebugOptions` `afterMatch`
           filter.

    :param \*\*args: If more control is needed, arguments can be passed in that
           are forwarded to the DebugOptions constructor. See the constructor
           for more details.

    :return: When no options are passed in, this returns the debug options object
             for this Pattern. If parameters are passed in, a DebugOptions object
             is created and associated with this Pattern.

    The debug option can be set using::

      >>> p = P(1).debug(True)
      >>> p = P(1) & 'show'  # Same as True
      >>> p = 'hide' & P(1)  # Same as False
    """

    if debugOpt is None and len(args) == 0: return self.dbg

    if debugOpt is not None:

      # Check if this is an object that supports the debug interface
      def isDebugHandlerObject(obj):
        hasInterfaceFn = lambda fn: hasattr(obj, fn) and callable(getattr(obj, fn))
        return hasInterfaceFn("beforeMatch") and hasInterfaceFn("afterMatch")

      if isDebugHandlerObject(debugOpt):
        self.dbg = debugOpt
        return self
      elif callable(debugOpt):
        self.dbg = DebugOptions(afterMatchFilter=debugOpt)
        return self

      optMap = {True:'show', False:'hide'}
      if debugOpt in optMap: debugOpt = optMap[debugOpt]

      # Check if the debugOpt matches one of the registered filters
      if debugOpt in DebugOptions.filters.keys(): args['matchFilter'] = debugOpt

    self.dbg = DebugOptions(**args)
    return self

  # ----------------------------------------------------------------------------

  def setName(self, name):
    """
    Set the name for a pattern object. When debugging, the name is printed in
    the debugging output in place of the Pattern specification. It is also used
    by the :class:`Tokenizer` class.

    :param name: The name for the Pattern.
    :return: The Pattern object. Allows chaining of commands.

    >>> p = P(1).setName('test 1')
    >>> p.name
    'test 1'
    >>> p = 'test 2' | P(1)
    >>> p.name
    'test 2'
    >>> p = P(1) | 'test 3'
    >>> p.name
    'test 3'
    """
    self.name = name
    return self

  # ----------------------------------------------------------------------------

  def _containsPatterns(self):
    """
    Indicate whether this is a container of other patterns.

    :return: True if this contains other Patterns, or False if not.

    >>> notAcontainer = P(1)
    >>> isAcontainer  = P(1) + P(1)
    >>> notAcontainer._containsPatterns()
    False
    >>> isAcontainer._containsPatterns()
    True
    """
    return False

  # ----------------------------------------------------------------------------

  def match(self, string, index=0, context=None):
    """
    Match the `Pattern` against the *string* starting at the given *index*. Note
    that :class:`Pattern` implements the `__call__` method which forwards calls
    to this function.

    :param string: A string to match.
    :param index:  The location in the string to look for the given pattern.
    :param context: Store stack information and information that is passed
           forward during match operations.
    :return: A :class:`Match` object if the pattern succeeds, or None if the
             pattern fails.

    >>> p = P('t')   # Match the 't' character
    >>> p.match('test')
    t
    >>> p('test')  # Equivalent to call above
    t
    """
    return None

  # ----------------------------------------------------------------------------

  @staticmethod
  def _positiveIndex(string, index, msg="Invalid index"):
    """
    Get the string index as a positive value. A negative index is calculated
    from the end of the string. If the index is outside the string bounds, an
    Exception is raised if msg is set. Otherwise the index at start or end of
    the string is returned.

    :param string: A string to match.
    :param index:  The location in the string to look for the given pattern.
    :param msg:    Message included in a ``ValueError`` exception if the index
                   is invalid

    >>> Pattern._positiveIndex("testing", -3)
    4
    >>> Pattern._positiveIndex("testing", 3)
    3
    """
    sz = len(string)
    if index >= 0:
      if index > sz and msg: raise ValueError(msg)
      return sz if index > sz else index

    idx = sz + index
    if idx < 0 and msg: raise ValueError(msg)
    return 0 if idx < 0 else idx

  # ----------------------------------------------------------------------------

  def _addPrn(self, toWrap):
    """
    Add parenthesis to the ``toWrap`` item if the precedence is higher than the
    current object.
    """
    if toWrap.name is not None:
      return "<{0}>".format(toWrap.name)

    getPrecedence = lambda obj: obj.precedence if hasattr(obj, 'precedence') else 101
    toWrapPrecedence = getPrecedence(toWrap)

    if toWrapPrecedence > self.precedence:
      return "({0})".format(repr(toWrap))
    elif toWrapPrecedence == self.precedence and type(toWrap) is not type(self):
      return "({0})".format(repr(toWrap))
    return repr(toWrap)

  # ----------------------------------------------------------------------------

  def __ror__(self, name):
    """
    ``"<name>"` | ptn`

    Used to set the name of a :class:`Pattern` object.

    :returns: The original pattern.
    """
    return self.__or__(name)

  # ----------------------------------------------------------------------------

  def __or__(self, name):
    """
    Sets the name of a :class:`Pattern` object.

    :param name: The name to use for this pattern
    :returns: The original pattern.

    >>> p = 'test' | P(1)
    >>> p.name
    'test'
    """
    self.setName(name)
    return self

  # ----------------------------------------------------------------------------

  def __rand__(self, debug_opt):
    """
    Set debug option for the pattern.

    :param debug_opt: See
    :return: Pattern with debug option set

    Hide the pattern object::

      p = False & P(1)
    """
    return self.__and__(debug_opt)

  # ----------------------------------------------------------------------------

  def __and__(self, debugOpt):
    """
    Set debug option for the pattern.

    :param debugOpt: Set debug options for the pattern.
    :return: The pattern with debug option set.

    Hide the pattern object::

      p = P(1) & 'hide'
    """
    self.debug(debugOpt)
    return self

  # ----------------------------------------------------------------------------

  def __div__(self, other):
    """

    :param other:
    :return:
    """

    if callable(other):
      return PatternFnWrap(self, other)
    elif isinstance(other, tuple) and len(other) == 2 and isinstance(other[0], int):
      return PatternCaptureN(self, *other)
    elif isinstance(other, int):
      return PatternCaptureN(self, other)
    raise ValueError("Invalid div expression for pattern.")

  # ----------------------------------------------------------------------------

  def __mul__(self, other):
    """
    Match patterns in order.

    :returns: A :class:`PattternAnd` object.

    >>> p = P('t') * P('e')
    >>> p('test')
    te
    """
    return PatternAnd(self, other)

  # ----------------------------------------------------------------------------

  def __rmul__(self, other):
    """
    Match patterns in order. Called when the first object in list is not a
    :class:`Pattern` object. The first object can be an integer or string and
    will be used to construct a :class:`P` pattern object.

    :returns: A :class:`PattternAnd` object.

    >>> p = 1*P("est")
    >>> p('test')
    test
    >>> p('pest')
    pest
    """
    return PatternAnd(other, self)

  # ----------------------------------------------------------------------------

  def __add__(self, other):
    """
    Matches the first pattern, or if that fails the second pattern.

    :returns: A :class:`PatternOr` object.

    >>> p = P('t') + P('p')
    >>> p('pop')
    p
    >>> p('top')
    t
    """
    return PatternOr(self, other)

  # ----------------------------------------------------------------------------

  def __radd__(self, other):
    """
    Matches *ptn1* or (if this fails) *ptn*.

    :returns: A :class:`PatternOr` object.

    >>> p = 'cat' + P('dog')
    >>> p('cat')
    cat
    >>> p('dog')
    dog
    """
    return PatternOr(other, self)

  # ----------------------------------------------------------------------------

  def __sub__(self, other):
    """
    Matches first pattern if second pattern does not match. This allows cases to
    be excluded from the *ptn* match.

    :returns: A pattern object.

    >>> p = P(3)-P('t')
    >>> p('pop')
    pop
    >>> p('top') is None
    True
    """
    return PatternAnd(PatternNot(other), self)

  # ----------------------------------------------------------------------------

  def __rsub__(self, other):
    """
    Matches first pattern if second pattern does not match. This allows cases to
    be excluded from the *ptn* match.

    :returns: A pattern object.
    """
    return PatternAnd(PatternNot(self), other)

  # ----------------------------------------------------------------------------

  def __neg__(self):
    """
    The match succeeds as long as the pattern does not succeed. No string input
    is consumed in the resulting :class:`Match`.

    :returns: A PatternNot object.

    >>> p = -P('Bob')
    >>> p('Bob') is None
    True
    """
    return PatternNot(self)

  # ----------------------------------------------------------------------------

  def __pow__(self, n):
    """
    If power ``n`` is positive, match at least ``n`` copies of the pattern. If
    ``n`` is negative, match at most ``n`` copies of the ``ptn``. If ``n`` is
    an integer in an array, matches exactly ``n`` occurrences.

    :returns: A PatternRepeat object.

    >>> p = P('t')**2
    >>> p('ttt')
    ttt
    >>> p = P('t')**-2
    >>> p('t')
    t
    >>> p = P('t')**[2]
    >>> p('ttt')
    tt
    """
    return PatternRepeat(self, n)

  # ----------------------------------------------------------------------------

  def __invert__(self):
    """
    A look ahead operation to whether the string matches ``ptn``. This consumes no
    input.

    :returns: A PatternLookAhead object.

    >>> p = ~P('test')
    >>> len(p('test')) == 0
    True
    """
    if isinstance(self, PatternLookAhead): return self
    return PatternLookAhead(self)

  # ----------------------------------------------------------------------------

  def __call__(self, string, index=0, context=None):
    """
    Shorthand for calling :func:`match(string[, index])`.

    :param string: A string to match.
    :param index:  The location in the string to look for the given pattern.
    :return: A :class:`Match` object if the pattern succeeds, or None if the
             pattern fails.
    """
    return self.match(string, index, context)

# ==============================================================================

class AtomicPattern(Pattern):
  """
  A Pattern that stands on its own (i.e., does not wrap one or more other
  Patterns).
  """
  precedence = 1

# ==============================================================================

class P(AtomicPattern):
  """
  The Pattern class matches a literal string or a specific number characters or
  checks against a user defined matcher function or matches against another
  Pattern.
  """

  # ----------------------------------------------------------------------------

  def __init__(self, value):
    """
    The *P* class accepts he following types:

    * *string* - Match against the literal string that is passed in.
    * *int*    - Match a given number of characters.
    * *fn*     - Match against a matcher function of form ``fn(string, index, context)``.
       The *fn* may return:

      * A :class:`Match` object with the start and end index set correctly for
        the match.
      * True to indicate a match that consumes no input.
      * An integer value that is greater than or equal to the start index and
        less than or equal to the length of the string. This indicates the end
        of the match.
      * False or None to indicate a failed match.

    :param value: The specification for this Pattern. See the options above.
    """
    Pattern.__init__(self)
    self.isValidValue(value)

    if isinstance(value, Pattern):
      self.matcher = self.match_ptn
      self.ptn     = value
      self.repr    = _repr_(value)

    elif isinstance(value, basestring):
      self.matcher = self.match_str
      self.string  = value
      self.size    = len(value)
      # TODO: Handle single quotes in representation.
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
      self.repr    = "P({0})".format(value.__name__) if hasattr(value, '__name__') else "P(fn)"

  # ----------------------------------------------------------------------------

  @staticmethod
  def isValidValue(value, msg = "Invalid arg for P(arg)"):
    """
    Verify that P(arg) is a valid arg. Raise an exception if not.
    """
    if isinstance(value, (Pattern, basestring, bool, int)): return True
    if callable(value): return True
    raise ValueError(msg)

  # ----------------------------------------------------------------------------

  @staticmethod
  def asPattern(pattern):
    """
    If item is a pattern, return the pattern. Otherwise return P(pattern)
    """
    return pattern if isinstance(pattern, Pattern) else P(pattern)

  # ----------------------------------------------------------------------------

  @ConfigBackCaptureString4match
  def match(self, string, index=0, context=None):
    """
    Match the given pattern
    :param context:
    """
    return self.matcher(string, index, context)

  # ----------------------------------------------------------------------------

  def match_ptn(self, string, index=0, context=None):
    """
    Matches the pattern passed in.

    >>> p = P(P("ab"))
    >>> p("abba")
    ab
    >>> p("abba",1) is None
    True
    """
    return self.ptn.match(string, index, context)

  # ----------------------------------------------------------------------------

  def match_str(self, string, index=0, context=None):
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

  # ----------------------------------------------------------------------------

  def match_n(self, string, index=0, context=None):
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

    :param string: The string to match
    :param index: The location in string to start match
    :param context: Information that is forwarded between matches.
    """
    if len(string) - index < self.n: return None
    return Match(string, index, index + self.n)

  # ----------------------------------------------------------------------------

  def match_neg(self, string, index=0, context=None):
    """
    Matches less than n characters only (end of string).

    >>> p = P(-3)
    >>> p("") == ""
    True
    >>> p("ab")
    ab
    >>> p("abc") is None
    True

    :param string: The string to match
    :param index: The location in string to start match
    :param context: Information that is forwarded between matches.
    """
    sz = len(string)
    if sz - index >= self.n: return None
    return Match(string, index, sz)

  # ----------------------------------------------------------------------------

  def match_TF(self, string, index=0, context=None):
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
    """
    if not self.TF or index > len(string): return None
    return Match(string, index, index)

  # ----------------------------------------------------------------------------

  def match_fn(self, string, index=0, context=None):
    """
    Call the function with signature:

      `match = fn(string, index, context)`

    The function can return one of the following:

    * A match object
    * An integer between `index` and the length of the string. This results in a
      match object ending at the given integer.
    * True results in a match object beginning and ending at the current index
    * False or any value not matching the above results in a match value of None.

    >>> p = P(lambda str, i, ctxt: i+2)
    >>> p("test")
    te
    >>> p("test",3) is None
    True
    >>> p = P(lambda str, i, ctxt: True)
    >>> p("test",4) == ""
    True

    :param string: The string to match
    :param index: The location in string to start match
    :param context: Information that is forwarded between matches.
    """
    match = self.fn(string, index, context)

    if match is True:
      return Match(string, index, index)
    if match in (False, None):
      return None
    if isinstance(match, Match):
      return match

    if isinstance(match, int):
        if index <= match and match <= len(string):
            return Match(string, index, match)
    return None

  # ----------------------------------------------------------------------------

  def __repr__(self):
    return self.repr

# ==============================================================================

class I(AtomicPattern):
  """
  Match case insensitive string.
  """

  # ----------------------------------------------------------------------------

  def __init__(self, string):
    Pattern.__init__(self)
    self.orig   = string
    self.string = string.lower()
    self.size   = len(string)

  # ----------------------------------------------------------------------------

  @ConfigBackCaptureString4match
  def match(self, string, index=0, context=None):
    """
    Match case insensitive string.

    >>> p = I("AcE")
    >>> p("Ace")
    Ace
    >>> p("ACE")
    ACE
    >>> p("ace")
    ace

    :param string: The string to match
    :param index: The location in string to start match
    :param context: Information that is forwarded between matches.
    """
    if len(string) - index < self.size: return None
    if string[index:index + self.size].lower() == self.string:
      return Match(string, index, index + self.size)
    return None

  # ----------------------------------------------------------------------------

  def __repr__(self):
    # TODO: Handle single quote in set
    return "I('%s')" % escapeStr(self.orig)

# ==============================================================================

class S(AtomicPattern):
  """
  Match any of a given set of characters.
  """

  # ----------------------------------------------------------------------------

  def __init__(self, set):
    Pattern.__init__(self)
    if not isinstance(set, basestring):
      raise ValueError("The arg must be a string in S(arg)")
    self.set = set

  # ----------------------------------------------------------------------------

  @ConfigBackCaptureString4match
  def match(self, string, index=0, context=None):
    """
    Match character in the given set.

    >>> p = S("ace")
    >>> p("a")
    a
    >>> p("b") is None
    True
    >>> p("abc",2)
    c

    :param string: The string to match
    :param index: The location in string to start match
    :param context: Information that is forwarded between matches.
    """
    if len(string) - index < 1: return None
    if string[index] not in self.set: return None
    return Match(string, index, index + 1)

  # ----------------------------------------------------------------------------

  def __repr__(self):
    # TODO: Handle single quote in set
    return "S('%s')" % escapeStr(self.set)

# ==============================================================================

class R(AtomicPattern):
  """
  Match characters in any of the given ranges. Each range is comprised of two
  characters where the ascii value of a character must be within the range of
  the two characters to be a match. Any number of ranges can be specified within
  the range object.
  """

  # ----------------------------------------------------------------------------

  def __init__(self, *ranges):
    Pattern.__init__(self)
    self.ranges = ranges
    for range in ranges:
      if len(range) != 2: raise ValueError("Ranges must have two values: %s" % range)
      if range[0] > range[1]:
        raise ValueError("Lower range value must be less than upper range value: %s" % range)

  # ----------------------------------------------------------------------------

  @ConfigBackCaptureString4match
  def match(self, string, index=0, context=None):
    """
    Matches any character in the given set of ranges.

    >>> p = R("AZ","az")
    >>> p("a")
    a
    >>> p("Q")
    Q
    >>> p("1") is None
    True

    :param string: The string to match
    :param index: The location in string to start match
    :param context: Information that is forwarded between matches.
    """
    if len(string) - index < 1: return False

    chr = string[index]
    for range in self.ranges:
      if range[0] <= chr and chr <= range[1]:
          return Match(string, index, index+1)
    return None

  # ----------------------------------------------------------------------------

  def __repr__(self):
    # TODO: Handle single quote in range values
    return "R(%s)" % (",".join(["'{0}'".format(escapeStr(range)) for range in self.ranges]))

# ===============================================================================

class SOL(AtomicPattern):
  """
  Check if his is the Start of Line (SOL).
  """

  def __init__(self):
    Pattern.__init__(self)

  # ----------------------------------------------------------------------------

  @ConfigBackCaptureString4match
  def match(self, string, index=0, context=None):
    """
    Match the start of a line.

    :param context:
    :param string: The string to match
    :param index: The index to start at
    :return: A match object. No characters are consumed.

    >>> p = SOL()
    >>> p.match("test\\n123\\n") == ""
    True
    >>> p.match("test\\n123\\n",1) is None
    True
    >>> p.match("test\\n123\\n",5) == ""
    True
    >>> p.match("test\\n123\\n",6) is None
    True
    >>> p.match("test\\n123\\n",9) == ""
    True
    """
    if index == 0 or string[index-1] == '\n':
      return Match(string, index, index)
    if string[index-1] == '\r' and (index == len(string) or string[index] != '\n'):
      return Match(string, index, index)
    return None

  # ----------------------------------------------------------------------------
  def __repr__(self):
    return "SOL()"

# ==============================================================================

class EOL(AtomicPattern):
  """
  Detect whether the current position is at the end of a line.
  """

  # ----------------------------------------------------------------------------

  def __init__(self):
    Pattern.__init__(self)

  # ----------------------------------------------------------------------------

  @ConfigBackCaptureString4match
  def match(self, string, index=0, context=None):
    """
    Detect whether the current position is at the end of a line.

    :param context:
    :param string: The string to compare against
    :param index: The location to check.
    :return: A match object that consumes no input.

    >>> p = EOL()
    >>> p.match("") == ""
    True
    >>> p.match("   \\r\\n",2) is None
    True
    >>> p.match("   \\r\\n",3) == ""
    True
    >>> p.match("   \\r\\n",4) is None
    True
    >>> p.match("\\n",0) == ""
    True
    """

    if index == len(string) or string[index] == '\r':
      return Match(string, index, index)
    if string[index] == '\n' and (index == 0 or string[index-1] != '\r'):
      return Match(string, index, index)
    return None

  # ----------------------------------------------------------------------------

  def __repr__(self):
    return "EOL()"

# ==============================================================================
# Captures
# ==============================================================================

class Capture(Pattern):
  precedence = 1

# ==============================================================================

class C(Capture):
  """
  Capture a pattern
  """

  # ----------------------------------------------------------------------------

  def __init__(self, pattern):
    """
    :param pattern: The pattern to capture.
    """
    Pattern.__init__(self)
    self.pattern = P.asPattern(pattern)

  # ----------------------------------------------------------------------------

  def _containsPatterns(self):
    """
    Indicate that this does contain patterns.
    :return: True
    """
    return True

  # ----------------------------------------------------------------------------

  def getPatterns(self):
    """
    Get the pattern associated with this group capture
    :return: The contained pattern in a list
    """
    return [self.pattern]

  # ----------------------------------------------------------------------------

  @ConfigBackCaptureString4match
  def match(self, string, index=0, context=None):
    """
    Add a Pattern match to the list of Captures.

    :param string: The string to match
    :param index: The location in string to start match
    :param context: Information that is forwarded between matches.

    >>> p = C(C(P(2))*P(1))
    >>> match = p("abcd")
    >>> match.getCapture(0)
    'abc'
    >>> match.getCapture(1)
    'ab'
    """

    match = self.pattern.match(string, index, context)
    if isinstance(match, Match):
      match.captures.insert(0, str(match))
    return match

  # ----------------------------------------------------------------------------

  def __repr__(self):
    return "C(%s)" % _repr_(self.pattern)

# ==============================================================================

class Cb(AtomicPattern):
  """
  Backcapture
  """

  # ----------------------------------------------------------------------------

  def __init__(self, name, pattern=None, captureIndex=None):
    """
    Match a previously captured value (i.e., a back capture).

    :param name: The name to store the back capture under for later reference.
    :param pattern: The pattern to match. The backcapture will be the full match
           if captureIndex is None, or the indicated capture index if the index
           is specified.
    :param captureIndex: The index of the captured item to use for the backcapture
           or None if the whole string is to be used.
    """
    Pattern.__init__(self)
    self.capname = name
    self.pattern = P.asPattern(pattern) if pattern is not None else None
    self.captureIndex = captureIndex

  # ----------------------------------------------------------------------------

  def _containsPatterns(self):
    """
    Indicate that this does contain patterns.
    :return: True
    """
    return self.pattern is not None

  # ----------------------------------------------------------------------------

  def getPatterns(self):
    """
    Get the pattern associated with this group capture
    :return: The contained pattern in a list
    """
    return [self.pattern]

  # ----------------------------------------------------------------------------

  @ConfigBackCaptureString4match
  def match(self, string, index=0, context=None):
    """
    :param string: The string to match
    :param index: The location in string to start match
    :param context: Information that is forwarded between matches.

    >>> p = Cb("test",P("cat")+P("dog")) * P(" ") * Cb("test")
    >>> p.match("dog dog")
    dog dog
    >>> p.match("cat cat")
    cat cat
    >>> p.match("cat dog") == None
    True
    >>> p = Cb("quote", S("\\"'")) * C((1-Cb("quote"))**0) * Cb("quote")
    >>> p.match("'Matched quoted string' but not extra stuff").captures[0]
    'Matched quoted string'
    >>> p.match('"Quoted String" without extra stuff').captures[0]
    'Quoted String'
    """
    if self.pattern is None:
      tomatch = string.getNamedCapture(self.capname)
      return P(tomatch).match(string, index, context)
    else:
      match = self.pattern.match(string, index, context)
      if isinstance(match, Match):
        value = match.getValue() if self.captureIndex is None else match.getCapture(self.captureIndex)
        string.addNamedCapture(self.capname, value)
    return match

  # ----------------------------------------------------------------------------

  def __repr__(self):
    # TODO: handle single quote in name
    if self.pattern is None:
      return "Cb('{0}')".format(self.capname)
    return "Cb('{0}',{0})".format(self.capname, _repr_(self.pattern))

# ==============================================================================

class Cc(Capture):
  """
  Capture a constant value.
  """

  # ----------------------------------------------------------------------------

  def __init__(self, value):
    Pattern.__init__(self)
    self.value = value

  # ----------------------------------------------------------------------------

  @ConfigBackCaptureString4match
  def match(self, string, index=0, context=None):
    """
    Capture the specified value.

    >>> p = Cc("test")
    >>> match = p("")
    >>> match[0]
    'test'

    :param string: The string to match
    :param index: The location in string to start match
    :param context: Information that is forwarded between matches.
    """
    return Match(string, index, index)._addCapture(self.value)

  # ----------------------------------------------------------------------------

  def __repr__(self):
    return 'Cc("%s")' % escapeStr(self.value)

# ==============================================================================

class Cg(Capture):
  """
  Group and contained Captures into a single capture. If there are no captures,
  the single capture will be an empty array.
  """

  # ----------------------------------------------------------------------------

  def __init__(self, pattern):
    """
    :param pattern: The pattern to match. Any captures will be grouped into a
           single capture.
    """
    Pattern.__init__(self)
    self.pattern = pattern

  # ----------------------------------------------------------------------------

  def _containsPatterns(self):
    """
    Indicate that this does contain patterns.
    :return: True
    """
    return True

  # ----------------------------------------------------------------------------

  def getPatterns(self):
    """
    Get the pattern associated with this group capture
    :return: The contained pattern in a list
    """
    return [self.pattern]

  # ----------------------------------------------------------------------------

  @ConfigBackCaptureString4match
  def match(self, string, index=0, context=None):
    """
    Group the contained captures into a single capture.

    :param string: The string to match
    :param index: The location in string to start match
    :param context: Information that is forwarded between matches.

    :Examples:

    >>> p = Cg(C(P(1)) * C(P(1)))
    >>> p("Test").getCapture(0)
    ['T', 'e']
    >>> p("b") is None
    True
    """

    match = self.pattern.match(string, index, context)
    if not isinstance(match, Match): return match

    match.captures = [match.captures]
    return match

  # ----------------------------------------------------------------------------

  def __repr__(self):
    return "Cg({0})".format(_repr_(self.pattern))

# ==============================================================================

class Cs(Capture):
  """
  Capture values from a stack
  """

  # ----------------------------------------------------------------------------

  def __init__(self, stack, n=1, pop_from_stack=False):
    """
    Capture values from a stack.

    :param stack: The name of the stack to capture values from.
    :param n: The number of values from the stack to add as captures. If
           the value is 'None' all values from the stack are added as captures.
           (Default 1).
    :param pop_from_stack: Flag to indicate if the values put in the capture
           list should be popped from the stack (False by default).
    """
    if n < 1 and n is not None: raise ValueError("For Cs(n), n must be a positive integer.")

    Pattern.__init__(self)
    self.stack          = stack
    self.n              = n
    self.pop_from_stack = pop_from_stack

  # ----------------------------------------------------------------------------

  @ConfigBackCaptureString4match
  def match(self, string, index=0, context=None):
    """
    Capture values from a stack

    :param string: The string to match against.
    :param index: The current location in the string.
    :param context: Information that is forwarded between matches.
    :return: A match object stack values added as captures.

    :Examples:

    >>> p = Sc('test',Cc('1')*Cc('2')*Cc('3')) * Cs('test')
    >>> match = p.match("")
    >>> match.captures
    ['3']
    >>> match.context.getStack('test')[0:]
    ['1', '2', '3']

    >>> p = Sc('test',Cc('1')*Cc('2')*Cc('3')) * Cs('test', 2, pop_from_stack=True)
    >>> match = p.match("")
    >>> match.captures
    ['2', '3']
    >>> match.context.getStack('test')[0:]
    ['1']
    """
    match = Match(string, index, index)

    stack = context.getStack(self.stack)
    if stack is None or len(stack) == 0: return match

    n = len(stack) if self.n is None else self.n
    stack_items = stack.pop(n) if self.pop_from_stack else stack[-n:]
    match.captures.extend(stack_items)

    return match

  # ----------------------------------------------------------------------------

  def __repr__(self):
    args = ["'{0}'".format(self.stack)]
    if self.n != 1: args.append('n={0}'.format(self.n))
    if self.pop_from_stack: args.append('pop_from_stack={0}'.format(self.pop_from_stack))
    return "Cs({0})".format(", ".join(args))

# ==============================================================================

class Cl(Capture):
  """
  Capture the current line number.
  """

  # ----------------------------------------------------------------------------

  def __init__(self):
    Pattern.__init__(self)

  # ----------------------------------------------------------------------------

  @ConfigBackCaptureString4match
  def match(self, string, index=0, context=None):
    """
    Capture the line number at the given index.

    :param string: The string to match against
    :param index: The index for which to get the line number
    :param context: Information that is forwarded between matches.
    :return: A match object with the line number added to the captures

    :Example:

    >>> p = Cl()
    >>> p("\\n\\n\\n\\n\\n\\n\\n\\n",3).getCapture(0)
    4
    """

    line = string.getLineNumber(index)
    return Match(string, index, index)._addCapture(line)

  # ----------------------------------------------------------------------------

  def __repr__(self):
    return "Cl()"

# ==============================================================================

class Cp(Capture):
  """
  Capture the current position.
  """

  # ----------------------------------------------------------------------------

  def __init__(self):
    Pattern.__init__(self)

  # ----------------------------------------------------------------------------

  @ConfigBackCaptureString4match
  def match(self, string, index=0, context=None):
    """
    Capture the current position in the string (index value).

    :param string: The string to match
    :param index: The location in string to start match
    :param context: Information that is forwarded between matches.

    >>> p = Cp()
    >>> p("test",3).getCapture(0)
    3
    >>> p("test",1).getCapture(0)
    1
    """
    return Match(string, index, index)._addCapture(index)

  # ----------------------------------------------------------------------------

  def __repr__(self):
    return "Cp()"

# ==============================================================================

class Col(Capture):
  """
  Capture the column (distance since last newline).
  """

  # ----------------------------------------------------------------------------

  def __init__(self):
    Pattern.__init__(self)

  # ----------------------------------------------------------------------------

  @ConfigBackCaptureString4match
  def match(self, string, index=0, context=None):
    """
    Capture the column for the current index (distance past last newline)

    :param string: The string to match
    :param index: The location in string to start match
    :param context: Information that is forwarded between matches.
    :return: A match object that consumes no characters, but adds a column
             capture.

    >>> p = Col()
    >>> #        0  123  456789
    >>> #                012345
    >>> p.match("\\n  \\n  Test",9).getCapture(0)
    5
    """
    match = Match(string, index, index)
    if index == 0: return match._addCapture(0)

    # Look backwards until the end of a line is found.
    for i in xrange(index-1, -1, -1):
      if string[i] not in ('\r','\n'): continue
      return match._addCapture(index - 1 - i)
    return match._addCapture(index)

  # ----------------------------------------------------------------------------

  def __repr__(self):
    return "Col()"

# ==============================================================================
# Captures
# ==============================================================================

class StackPtn(Pattern):
  precedence = 1

# ==============================================================================

class Sc(StackPtn):
  """
  Move captures to the specified stack in the context.
  """

  # ----------------------------------------------------------------------------

  def __init__(self, stack, pattern):
    """

    :param stack: The name of the stack in the context to move captures to.
    :param pattern: The pattern to use. Typically will have captures.
    """
    Pattern.__init__(self)
    self.stack = stack
    self.pattern = P.asPattern(pattern)

  # ----------------------------------------------------------------------------

  def _containsPatterns(self):
    """
    Indicate that this does contain patterns.
    :return: True
    """
    return True

  # ----------------------------------------------------------------------------

  def getPatterns(self):
    """
    Get the pattern associated with this group capture
    :return: The contained pattern in a list
    """
    return [self.pattern]

  # ----------------------------------------------------------------------------

  @ConfigBackCaptureString4match
  def match(self, string, index=0, context=None):
    """
    Move the captured values to the specified stack.

    :param string: The string to match
    :param index: The location in string to start match
    :param context: Information that is forwarded between matches.
    :return: A match object that consumes no characters, but adds a column
             capture.

    :Example:

    >>> p = Sc('test',Cc('one')*Cc('two'))
    >>> match = p.match("")
    >>> match.context.getStack('test')[0:]
    ['one', 'two']
    """

    match = self.pattern.match(string, index, context)
    if not isinstance(match, Match): return match

    if match.hasCaptures():
      context.extend(self.stack, match.captures)
      match.captures = []
      #print "{0}: {1}".format(self.stack, context.getStack(self.stack))

    return match

  # ----------------------------------------------------------------------------

  def __repr__(self):
    # TODO: Support single quotes in stack name
    return "Sc('{0}', {1})".format(self.stack, _repr_(self.pattern))

# ==============================================================================

class Sp(StackPtn):
  """
  Pop captures from the stack
  """

  # ----------------------------------------------------------------------------

  def __init__(self, stack, n=1):
    """

    :param stack: The name of the stack to pop values from.
    :param pattern: The number of values to pop.
    """
    Pattern.__init__(self)
    self.stack = stack
    self.n = n

  # ----------------------------------------------------------------------------

  @ConfigBackCaptureString4match
  def match(self, string, index=0, context=None):
    """
    Pop values from the stack.

    :param string: The string to match
    :param index: The location in string to start match
    :param context: Information that is forwarded between matches.
    :return: A match object that consumes no characters, but adds a column
             capture.
    """

    match = Match(string, index, index)
    stack = context.getStack(self.stack)
    for i in range(self.n): stack.pop()
    return match

  # ----------------------------------------------------------------------------

  def __repr__(self):
    # TODO: Support single quotes in stack name
    return "Sp('{0}', {1})".format(self.stack, "" if self.n == 1 else self.n)

# ==============================================================================

class Sm(StackPtn):
  """
  Match a value in the Stack with one in the string passed to match, or check
  for a specific string on the match stack. Checking for a specific string on
  the stack at a given location is useful for controling the parsing logic
  based on state stored on the stack.
  """

  # ----------------------------------------------------------------------------

  def __init__(self, stack, n=-1, expected=None):
    """

    :param stack: The name of the stack to pop values from.
    :param n: Index of the value to match (-1 by default).
    :param expected: If this is passed in, the stack is checked to see
           if the value on the stack matches the expected value. If this is
           None, the string passed to match is compared to see if it matches
           the value on the stack at index n.
    """
    Pattern.__init__(self)
    self.stack    = stack
    self.n        = n
    self.expected = expected

  # ----------------------------------------------------------------------------

  @ConfigBackCaptureString4match
  def match(self, string, index=0, context=None):
    """
    Match value on the stack.

    :param string: The string to match.
    :param index: The location in string to start match.
    :param context: Information that is forwarded between matches.
    :return: A match object that consumes no characters, but adds a column
             capture.

    :Example:

    >>> p = Sc("my_stack",Cc("test")*Cc("ing"))*Sm("my_stack",0)*Sm("my_stack")
    >>> p("testing")
    testing
    >>> p("tester") == None
    True

    >>> p = Sc("items",Cc("one")*Cc("two"))*Sm("items",0,"one")*Sm("items",1,"two")
    >>> match = p('')
    >>> isinstance(match, Match)
    True
    """

    stack = context.getStack(self.stack)

    if stack is None and self.expected is not None: return None
    if not stack.isValidIndex(self.n): return None

    stack_item = stack[self.n]

    # Match the stack item against the expected value
    if self.expected:
      if self.expected == stack_item:
        return Match(string, index, index)
      return None

    # Match the item on the stack against the string
    if isinstance(stack_item, basestring):
      match = P(stack_item).match(string, index, context)
      return match

    return None

  # ----------------------------------------------------------------------------

  def __repr__(self):
    # TODO: Support single quotes in stack name
    return "Sm('{0}', {1})".format(self.stack, "" if self.n == 1 else self.n)

# ==============================================================================

class Ssz(StackPtn):
  """
  Get the stack size or match only if it has a given size
  """

  # ----------------------------------------------------------------------------

  def __init__(self, stack, n=None):
    """

    :param stack: The name of the stack get or check the size of.
    :param n: An optional stack size.
    """
    Pattern.__init__(self)
    self.stack = stack
    self.n = n

  # ----------------------------------------------------------------------------

  @ConfigBackCaptureString4match
  def match(self, string, index=0, context=None):
    """
    Capture the stack size or check that the stack matches a given size.

    :param string: The string to match
    :param index: The location in string to start match
    :param context: Information that is forwarded between matches.
    :return: A match object that consumes no characters, but adds a column
             capture.
    """

    stack = context.getStack(self.stack)
    sz = 0 if stack is None else len(stack)
    if self.n is None:
       match = Match(string, index, index)._addCapture(sz)
    elif self.n != sz:
      match = None
    else:
      match = Match(string, index, index)

    return match

  # ----------------------------------------------------------------------------

  def __repr__(self):
    # TODO: Support single quotes in stack name
    if self.n is None: return "Ssz('{0}')".format(self.stack)
    return "Ssz('{0}', {1})".format(self.stack, self.n)

# ==============================================================================
# Pattern Operators
# ==============================================================================

class CompositePattern(Pattern):

  # ----------------------------------------------------------------------------

  def __init__(self):
    Pattern.__init__(self)
    self.patterns = []

  # ----------------------------------------------------------------------------

  def _containsPatterns(self):
    return True

  # ----------------------------------------------------------------------------

  def getPatterns(self):
    return self.patterns

# ===============================================================================

class V(CompositePattern):
  precedence = 1

  # ----------------------------------------------------------------------------

  def __init__(self, name):
    """
    :param name: The is a pattern place holder. The name is the name of this
                 pattern. The associated Pattern will be set later.
    """
    CompositePattern.__init__(self)
    self.setName(name)

  # ----------------------------------------------------------------------------

  def setPattern(self, pattern):
    """
    Set the pattern for this V object.
    :param pattern: The pattern associated with this V object
    """
    self.patterns.insert(0, pattern)

  # ----------------------------------------------------------------------------

  def match(self, string, index=0, context=None):
    if len(self.patterns) > 0:
      return self.patterns[0].match(string, index, context)
    return None

  # ----------------------------------------------------------------------------

  def __repr__(self):
    return "V('{0}')".format(self.name)

# ==============================================================================

def setVs(pattern, Vs=None, replace=False):
  """
  Set the pattern for V (pattern place holder) objects within this Pattern. Note
  that if the pattern on which `setVs` is called contains includes the named pattern
  associated with each pattern place holder object, then `setVs` can be called without
  passing in a replacement list since this named objects that are already in the
  pattern will be used.

  :Example:

  This is an example of parsing a comma separated list of digits with parenthesis
  around sublists supported.

  >>> d = R('09')**1
  >>> p = d + '(' * V('P') * ')'  + V('P') * ',' * V('P') 
  >>> setVs(p, {'P' : p})
  >>> p.match("1,2,3,(4,5,(6))")
  '1,2,3,(4,5,(6))'

  :param pattern: A Pattern object (may contain other patterns)
  :param Vs: A dictionary of V objects to set, or an array of named Patterns. If this
         is not specified, then the pattern object is searched for named parameters,
         and the named parameters are used to replace the pattern place holder objects.
  :param replace: Replace the V objects with the associated Pattern (default False).
  :return: The updated (or replaced) Pattern
  """
  if not isinstance(pattern, Pattern): return pattern

  # Get all the patterns conatined in this pattern
  patterns = pattern.getPatterns() if pattern._containsPatterns() else []
  if Vs is None: Vs = patterns
        
  if isinstance(Vs, (list, tuple)):
    # Convert the named patterns to a distionary
    Vs = {ptn.name: ptn for ptn in Vs if ptn.name is not None}

  # If we get to a V object, set the value if it is defined.
  if isinstance(pattern, V):
    if pattern.name in Vs:
      if replace: return Vs[pattern.name]
      pattern.setPattern(Vs[pattern.name])
    return pattern

  # If this does not contain patterns return
  if not pattern._containsPatterns(): return pattern

  # Set the Vs for all contained patterns
  for i, ptn in enumerate(patterns):
    ptn = setVs(ptn, Vs, replace)
    if replace: patterns[i] = ptn

  return pattern

# ==============================================================================

class PatternFnWrap(CompositePattern):
  """
  Pass the match to the given function and return the match returned by the
  function
  """
  precedence = 6

  # ----------------------------------------------------------------------------

  def __init__(self, pattern, fn):
    CompositePattern.__init__(self)
    self.patterns.append(pattern)
    self.fn      = fn

  # ----------------------------------------------------------------------------

  @ConfigBackCaptureString4match
  def match(self, string, index=0, context=None):
    """

    :param string: String to match
    :param index: Index in string to start at
    :param context: Information forwarded between matches
    :return: None if pattern fails, or a match object returned by the function
             after receiving the pattern match object.

    :Example:

    >>> def fn(match): return match._addCapture("test")
    >>> p = P(3) / fn
    >>> p("Cat").captures
    ['test']
    """
    match = self.patterns[0].match(string, index, context)
    if match is None: return None

    return self.fn(match)

  # ----------------------------------------------------------------------------

  def __repr__(self):
    name = self.fn.__name__ if hasattr(self.fn,"__name__") else "<fn>"
    return "({0})/{1}".format(repr(self.patterns[0]), name)

# ===============================================================================

class PatternCaptureN(CompositePattern):
  """
  Keep the nth capture in the list of captures. If the capture does not exist,
  a default is used if specified or no captures are added.
  """
  precedence = 6

  # ----------------------------------------------------------------------------

  def __init__(self, pattern, n, default=None):
    """
    :param pattern: Pattern to apply to string starting at the given index.
    :param n: The capture to take from the pattern match.
    :param default: The default to use if the given capture is not present
    """
    CompositePattern.__init__(self)
    self.patterns.append(pattern)
    self.n       = n
    self.default = default

  # ----------------------------------------------------------------------------

  @ConfigBackCaptureString4match
  def match(self, string, index=0, context=None):
    """
    Get the nth capture of a pattern. If capture does not exist, use the default
    if specified, or include no captures in match that is returned.

    :param string: The string to match
    :param index: The location in string to start match
    :param context: Information that is forwarded between matches.
    :return:  A match with just the nth capture retained.

    :Example:

    >>> # Get second capture
    >>> p = (Cc("0")*Cc("1")*Cc("2"))/1
    >>> p("").getCapture(0)
    '1'
    >>> # Get last capture
    >>> p = (Cc("0")*Cc("1")*Cc("2"))/-1
    >>> p("").getCapture(0)
    '2'
    >>> # Sepcify capture index and default value - use a tuple (n, default)
    >>> p = (Cc("0")*Cc("1")*Cc("2"))/(3, "invalid capture")
    >>> p("").getCapture(0)
    'invalid capture'
    """

    match = self.patterns[0].match(string, index, context)
    if match is None: return None

    newmatch = Match(string, index, match.end)
    try:
      newmatch._addCapture(match.captures[self.n])
    except IndexError:
      if self.default is not None:
        newmatch._addCapture(self.default)

    return newmatch

  # ----------------------------------------------------------------------------

  def __repr__(self):
    n = self.n if self.default is None else "({0},{1})".format(self.n, self.default)
    return "({0})/{1}".format(repr(self.patterns[0]),n)

# ===============================================================================

class PatternAnd(CompositePattern):
  """
  Match pattern1 followed by pattern2.
  """
  precedence = 6

  # ----------------------------------------------------------------------------

  def __init__(self, pattern1, pattern2):
    """
    Match pattern1 followed by pattern2.

    :param pattern1: The first pattern to match
    :param pattern2: The second pattern to match
    """
    CompositePattern.__init__(self)
    if not isinstance(pattern1, Pattern) and not isinstance(pattern2, Pattern):
      raise ValueError("PatternAnd requires the first or second constructor item to be a Pattern")

    isValidValue = P.isValidValue
    isValidValue(pattern1, msg="For 'a*b', 'a' must be Pattern or int value")
    isValidValue(pattern2, msg="For 'a*b', 'b' must be Pattern or int value")

    asPattern = P.asPattern
    self.patterns = [asPattern(pattern1), asPattern(pattern2)]
    self.is_sub_and = False # Is this contained in another and operation
    self.is_not_ptn = isinstance(pattern1, PatternNot) # Indicate if this is (Ptn1 - Ptn)
    if self.is_not_ptn:
      self.precedence = 7

    if isinstance(pattern1, PatternAnd): pattern1.is_sub_and = True
    if isinstance(pattern2, PatternAnd): pattern2.is_sub_and = True

  # ----------------------------------------------------------------------------

  @ConfigBackCaptureString4match
  def match(self, string, index=0, context=None):
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

    :param string: The string to match
    :param index: The location in string to start match
    :param context: Information that is forwarded between matches.
    """

    MATCH = Match(string, index)
    # Make sure all the patterns match
    for pattern in self.patterns:
      match = pattern.match(string, index, context)
      if not isinstance(match, Match): return None
      MATCH._addSubmatch(match)
      index = match.end
    MATCH.end = index
    return MATCH

  # ----------------------------------------------------------------------------

  def __repr__(self):
    # Check if this is a NOT pattern (i.e., ptn1 - ptn2)
    if self.is_not_ptn:
      # Get the pattern contained by PatternNot since we will add the '-' manually
      notPtn = self.patterns[0].getPatterns()[0]
      return "%s - %s" % (self._addPrn(self.patterns[1]), self._addPrn(notPtn))
    else:
      return "{0}*{1}".format(self._addPrn(self.patterns[0]), self._addPrn(self.patterns[1]))

# ==============================================================================

class PatternOr(CompositePattern):
  """
  Look for the first pattern in the list that matches the string.
  """
  precedence = 7

  # ----------------------------------------------------------------------------

  def __init__(self, pattern1, pattern2):
    CompositePattern.__init__(self)
    if not isinstance(pattern1, Pattern) and not isinstance(pattern2, Pattern):
      raise ValueError("PatternOr requires the first or second constructor item to be a Pattern")

    isValidValue = P.isValidValue
    isValidValue(pattern1, msg="For 'a+b', 'a' must be Pattern or int value")
    isValidValue(pattern2, msg="For 'a+b', 'b' must be Pattern or int value")

    self.patterns = [P.asPattern(pattern1), P.asPattern(pattern2)]

  # ----------------------------------------------------------------------------

  @ConfigBackCaptureString4match
  def match(self, string, index=0, context=None):
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

    :param string: The string to match
    :param index: The location in string to start match
    :param context: Information that is forwarded between matches.
    """

    for pattern in self.patterns:
      match = pattern.match(string, index, context)
      if isinstance(match, Match): return match
    return None

  # ----------------------------------------------------------------------------

  def __repr__(self):
    return "{0} + {1}".format(self._addPrn(self.patterns[0]), self._addPrn(self.patterns[1]))

# ==============================================================================

class PatternNot(CompositePattern):
  """
  Verify that the text ahead does not match the pattern. The string index does
  not advance.
  """
  precedence = 5

  # ----------------------------------------------------------------------------

  def __init__(self, pattern):
    CompositePattern.__init__(self)
    P.isValidValue(pattern, msg ="Invalid '-ptn' expression")
    self.patterns.append(P.asPattern(pattern))

  # ----------------------------------------------------------------------------

  @ConfigBackCaptureString4match
  def match(self, string, index=0, context=None):
    """

    >>> p = -P("bob")
    >>> p("bob") is None
    True
    >>> p("fred") == ""
    True

    :param string: The string to match
    :param index: The location in string to start match
    :param context: Information that is forwarded between matches.
    """

    match = self.patterns[0](string, index, context)
    if not isinstance(match, Match): return Match(string, index, index)
    return None

  # ----------------------------------------------------------------------------

  def __repr__(self):
    return "-%s" % self._addPrn(self.patterns[0])

# ==============================================================================

class PatternRepeat(CompositePattern):
  """
  Repeat a pattern n or more times, n or less times, or exactly n times.
  """
  precedence = 4

  # ----------------------------------------------------------------------------

  def __init__(self, pattern, n):
    """
    :param pattern: The pattern to repeat
    :param n: The repeat rule:
      - For n positive, repeat at least n times.
      - For n negative, repeat at most n times.
      - For [n], with n positive, repeat exactly n times.
    """
    CompositePattern.__init__(self)

    if not isinstance(pattern, Pattern): raise ValueError("First value to PatternRepeat must be a pattern")
    matchExact = True if isinstance(n, list) else False
    if matchExact:
      if len(n) == 0: raise ValueError("In ptn**[n], n calue is missing")
      n = n[0]
    if not isinstance(n, (int,list)): raise ValueError("In ptn**n, n must be an integer value or [n]")

    self.patterns.append(pattern)

    if matchExact:
      self.matcher = self.match_n
      self.n = abs(n)
    elif n >= 0:
      self.matcher = self.match_at_least_n
      self.n = n
    else:
      self.matcher = self.match_at_most_n
      self.n = -n

  # ----------------------------------------------------------------------------

  @ConfigBackCaptureString4match
  def match(self, string, index=0, context=None):
    return self.matcher(string, index, context)

  # ----------------------------------------------------------------------------

  def match_n(self, string, index=0, context=None):
    """

    >>> p = S("abc")**[3]
    >>> p("ab") is None
    True
    >>> p("abcd")
    abc
    """
    MATCH = Match(string, index)
    cnt = 0
    for i in xrange(self.n):
      match = self.patterns[0].match(string, index, context)
      if not isinstance(match, Match): return None
      index = match.end
      MATCH._addSubmatch(match)
      MATCH._setEnd(index)
    return MATCH

  # ----------------------------------------------------------------------------

  def match_at_least_n(self, string, index=0, context=None):
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
      match = self.patterns[0].match(string, index, context)

      if not isinstance(match, Match):
        return MATCH._setEnd(index) if cnt >= self.n else None

      MATCH._addSubmatch(match)

      # No progress, so it matches infinite times
      if match.end == index: return MATCH._setEnd(index)

      cnt += 1
      index = match.end

  # ----------------------------------------------------------------------------

  def match_at_most_n(self, string, index=0, context=None):
    """

    >>> p = S("abc")**-3
    >>> p("") == ""
    True
    >>> p("abca")
    abc
    """
    MATCH = Match(string, index)
    for i in range(self.n):
      match = self.patterns[0].match(string, index, context)
      if not isinstance(match, Match): return MATCH._setEnd(index)
      MATCH._addSubmatch(match)
      index = match.end
    return MATCH._setEnd(index)

  # ----------------------------------------------------------------------------

  def __repr__(self):
    n = self.n
    if self.matcher == self.match_at_most_n: n = -n
    if self.matcher == self.match_n: n = "[{0}]".format(n)
    return "{0}**{1}".format(self._addPrn(self.patterns[0]), n)

# ==============================================================================

class PatternLookAhead(CompositePattern):
  """
  Check whether the pattern matches the string that follows without consuming the
  string
  """
  precedence = 5

  # ----------------------------------------------------------------------------

  def __init__(self, pattern):
    CompositePattern.__init__(self)
    P.isValidValue(pattern)
    self.patterns.append(P.asPattern(pattern))

  # ----------------------------------------------------------------------------

  @ConfigBackCaptureString4match
  def match(self, string, index=0, context=None):
    """

    >>> p = ~P("test")
    >>> p("testing") == ""
    True
    >>> p("This is a test", 10) == ""
    True
    >>> p("Failed") is None
    True

    :param string: The string to match
    :param index: The location in string to start match
    :param context: Information that is forwarded between matches.
    """
    match = self.patterns[0].match(string, index, context)
    if isinstance(match, Match): return match._setEnd(index)
    return None

  # ----------------------------------------------------------------------------

  def __repr__(self):
    return "~%s" % repr(self.patterns[0])

# ==============================================================================
# General patterns
# ==============================================================================

alpha       = R("az", "AZ")
digit       = R("09")
quote       = S("\"'")
whitespace  = S(" \t")
whitespace0 = whitespace**0  # 0 or more whitespace characters
whitespace1 = whitespace**1  # 1 or more whitespace characters
newline     = P("\r\n") + P("\r") + P("\n")

# ==============================================================================
# BackCaptureString
# ==============================================================================

class BackCaptureString(object):
  """
  This class is used to track the string that is being matched against and any
  back captures that are generated. Back captures are stored in a stack. Back
  captures that are added as part of a pattern that fails are removed from the
  stack.
  """

  # ----------------------------------------------------------------------------

  def __init__(self, string):
    self.string           = string
    self.backcaptures     = []
    self.startOfLineIndex = [0]
    self.stringSz         = len(string)
    # Pattern to find start of lines
    #self.line = (1 - newline) ** 0 * (newline) ** -1 * Cp()

  # ----------------------------------------------------------------------------

  def addNamedCapture(self, name, capture):
    """
    Add a named capture to the list of back captures.
    """
    self.backcaptures.append((name, capture))

  # ----------------------------------------------------------------------------

  def getNamedCapture(self, name):
    """
    Get a named capture from the list. The most recent capture of the given
    name is returned.
    """

    for i in xrange(self.getStackSize()-1,-1,-1):
      bcname, capture = self.backcaptures[i]
      if bcname == name: return capture

    raise IndexError("No backcapture was found for '{0}'".format(name))

  # ----------------------------------------------------------------------------

  def getStackSize(self):
    """
    Get the number of back captures
    """
    return len(self.backcaptures)

  # ----------------------------------------------------------------------------

  def setStackSize(self, size):
    """
    Set the stack back to the given size. If the stack is too large raise an
    Exception.
    """
    sz = len(self.backcaptures)
    if size == sz: return
    if sz < size: raise ValueError("The backcaptures stack is shorter than "
                                   "expected.")

    self.backcaptures = self.backcaptures[0:size]

  # ----------------------------------------------------------------------------

  def getColumnNumber(self, index):
    """
    Get the index of the start of the line in the `startOfLineIndex` array.

    :param index: The index in the string.
    :return: The index for the `startOfLineIndex` array that marks the start
             of the line containing the given index.
    """

    line = self.getLineNumber(index)
    col = index - self.startOfLineIndex[line-1]+1
    return col

  # ----------------------------------------------------------------------------

  def getLineNumber(self, index):
    """
    Get the line number at the given position in the string. The line numbers
    start with 1.

    :param index: The position in the string.
    :return: The line number associated with the position.
    """

    if index < 0 or self.stringSz < index:
      if index < 0:
        raise IndexError("Error getting line number for position. Index cannot "
                         "be less than 0")
      else:
        raise IndexError("Error getting line number for position. Index is "
                         "past the end of the string")

    # If the line number is already calculated. Find the line number.
    if index <= self.startOfLineIndex[-1]:
      if index == self.startOfLineIndex[-1]: return len(self.startOfLineIndex)

      # TODO: Make a more efficient lookup for line number.
      for i, startOfLine in enumerate(self.startOfLineIndex):
        if index < startOfLine: return i

    def nextnewline(idx):
      NOTFOUND = -2
      dat = {'idx':idx,'\r':idx-1,'\n':idx-1}
      def getnext(string):
        r, n, idx = (dat[i] for i in ('\r','\n','idx'))
        if r != NOTFOUND and r <= idx: r = string.find('\r', r+1); dat['\r'] = r == -1 and NOTFOUND or r
        if n != NOTFOUND and n <= idx: n = string.find('\n', n+1); dat['\n'] = n == -1 and NOTFOUND or n
        if n == NOTFOUND and r == NOTFOUND: return len(string)
        dat['idx'] = n+1 if n != NOTFOUND and (n < r or n == r+1 or r == NOTFOUND) else r+1
        return dat['idx']

      return getnext

    # Find start of lines till we get to index
    startOfLine = self.startOfLineIndex[-1]
    nextnl = nextnewline(startOfLine)
    while True:
      startOfLine = nextnl(self.string)

      # This if is just a precaution to make sure that we don't append indexes
      # less than the ones on the list.
      if startOfLine > self.startOfLineIndex[-1]:
        self.startOfLineIndex.append(startOfLine)
      if index < startOfLine:
        return len(self.startOfLineIndex) - 1
      if index == startOfLine:
        return len(self.startOfLineIndex)
    raise IndexError(
      "Unexpected error calculating line number for string position")

  # ----------------------------------------------------------------------------

  def __getitem__(self, index):
    if isinstance(index, (int,slice)):
      return self.string[index]

    return self.backcaptures[index]

  # ----------------------------------------------------------------------------

  def __getattr__(self, attr):
    return getattr(self.string, attr)

  # ----------------------------------------------------------------------------

  def __len__(self):
    return len(self.string)

  # ----------------------------------------------------------------------------

  def __repr__(self):
    return self.string

# ==============================================================================
# Match object
# ==============================================================================

class Match(object):
  """
  The ``Match`` object tracks the text that was matched by a PEG pattern, and
  provides access to any match captures.

  :ivar string: The original string that was matched.
  :ivar start: The location in the string where the pattern match starts.
  :ivar end: The location in the string where the pattern match ends.
  :ivar captures: The Pattern captures. Note that the ``match.getCapture(n)`` method
        is available to access captures, or simply ``match[n]``. ``len(match)``
        indicates the number of captures.
  """

  # ----------------------------------------------------------------------------

  def __init__(self, string, start, end=None):
    self.string   = string
    self.start    = start
    self.end      = end
    self.captures = []
    self.context  = None

  # ----------------------------------------------------------------------------

  def _setEnd(self, end):
    """
    Set the index of end of the match and return he current match object.
    """
    self.end = end
    return self

  # ----------------------------------------------------------------------------

  def getValue(self, default=None):
    """
    Get the string that was matched by the PEG pattern.
    """
    start, end = (self.start, self.end)
    return default if self.end is None else self.string[start:end]

  # ----------------------------------------------------------------------------

  def _addCapture(self, capture):
    """
    Add a capture or a submatch.
    """
    self.captures.append( capture )
    return self

  # ----------------------------------------------------------------------------

  def _setCaptures(self, captures):
    """
    Set the captures for this match.

    :param captures: A list object which becomes the captures list, or an object
                     which is added to a new captures list.
    :return: The match object
    """
    if isinstance(captures, list):
      self.captures = captures
    else:
      self.captures = [captures]
    return self

  # ----------------------------------------------------------------------------

  def _addSubmatch(self, match):
    """
    Extend the captures in the current match object with captures from a
    contained PEG pattern.
    """
    self.captures.extend(match.captures)
    return self

  # ----------------------------------------------------------------------------

  def hasCaptures(self):
    """
    :return: Return true if this Match object contains any captures.
    """
    return len(self.captures) > 0

  # ----------------------------------------------------------------------------

  def getCapture(self, index):
    """
    Get the capture at the specified index. If the index does not exist, throw
    an IndexError. Note that the number of captures for a Match object named
    ``match`` is given by ``len(match)``. Note that array syntax can be used
    with the Match object as a shorthand for calling this method. For example,
    ``match[1]`` is equivalent to ``match.getCapture(1)``.

    :param index: The index of the capture with the first capture being index
           0. A negative index is used to access values relative to the end of
           the array, with index -1 being the last capture value.
    :return: The requested capture value.
    """
    # TODO: Handles slices?
    if not self.hasCaptures() or -index < -len(self.captures) or len(self.captures) <= index:
      raise IndexError("Invalid capture index for Match")
    return self.captures[index]

  # ----------------------------------------------------------------------------

  def __getattr__(self, attr):
    return getattr(str(self), attr)

  # ----------------------------------------------------------------------------

  def __getitem__(self, key):
    """
    Get a capture from the Match object
    """
    if isinstance(key, int) and 0 <= key and key < len(self):
      return self.getCapture(key)
    raise IndexError("Invalid index for Match")

  # ----------------------------------------------------------------------------

  def __eq__(self, other):
    """
    Compare with strings or other Match objects. Check that the resulting value
    matches.
    """
    if isinstance(other, basestring):
      return str(self) == other

    if isinstance(other, Match):
      return str(self) == str(other)

  # ----------------------------------------------------------------------------

  def __len__(self):
    return len(self.captures)

  # ----------------------------------------------------------------------------

  def __repr__(self):
    return str(self)

  # ----------------------------------------------------------------------------

  def __str__(self):
    return self.getValue()

# ==============================================================================

def matchUntil(pattern, matchAfter=False):
  """
  Return a Pattern that matches any text until the given pattern is found. If
  the `matchAfter` parameter is True, the specified pattern is matched afterward.

  :param pattern: Find all text up the the given pattern.
  :param matchAfter: Indicate whether the pattern should be matched after it is
         found (default False).
  :return: A Pattern that matches all text up to the given pattern, and matches
         the pattern as well if `matchAfter` is True.
  """
  beforePattern = (1-pattern & 'hide')**0
  if not matchAfter: return beforePattern
  return beforePattern * pattern

# ==============================================================================
# Match processing functions
# ==============================================================================

def join(separator=""):
  """
  The join function returns a match handler function that can be used to join
  captures from a match. The format of the function that is returned is:

    `modified_match = fn(match)`

  This can be used in a pattern as follows:

  >>> p = C(1)**1 / join(",")
  >>> p.match("123").captures
  ['1,2,3']

  :param separator: The string to use to join the capture values (Empty sting by default)
  :return: The match object with the joined string as the only capture.
  """
  def joinfn(match):

    joined = separator.join(match.captures)
    match.captures = [joined]
    return match

  return joinfn

# ==============================================================================
# ==============================================================================

def match(pattern, subject, index=0, context=None):
  """
  """
  return pattern.match(subject, index, context)

# ==============================================================================

def _repr_(ptn, prnsCls=None):
  if ptn.name is not None:
    return "<{0}>".format(ptn.name)
  if callable(prnsCls):
    if prnsCls(ptn):
      return "({0})".format(repr(ptn))
  elif prnsCls and isinstance(ptn, prnsCls):
    return "({0})".format(repr(ptn))
  return repr(ptn)

# ==============================================================================

if __name__ == "__main__":
  import doctest
  doctest.testmod()
