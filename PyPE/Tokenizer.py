from __future__ import print_function
from .PyPE import Pattern, BackCaptureString
# ==============================================================================

class Grammar(object):
  """
  This class contains a :class:`Tokenizer` grammar, which is an ordered list of PyPE
  parsing patterns used to process a string. You can think of a grammar as an
  ordered list of active parsing instructions. The :class:`Tokenizer` will test each pattern
  against the string being processed in order. The grammar accepts the first pattern
  that matches the string at the current string location. If the pattern is assigned
  a name using the syntax `'<name>'|ptn` then (name, match) is returned from the 
  :class:`Tokenizer`. If the pattern does not have an assigned name, then no value
  is returned. After a pattern succeeds, the grammar is tested again starting at 
  the end of the last location processed. If none of the patterns succeed, the 
  :class:`Tokenizer` stops.   
  
  Note that every pattern needs to consume at least one character or the :class:`Tokenizer`
  will stop since no progress will be made in parsing it no text is consumed.

  Each item in the grammar can be a PyPE pattern, or a list or tuple the is used
  to switch to a new grammar. The list or tuple should contain three items:

  1. A pattern that marks the start of a new grammar. This is not required to
     consume text, but may. The result will be returned as a token as with other
     pattern unless the new grammar pattern is unnamed.
  2. The string name of the new grammar. This must be one of the grammars
     registered with the Tokenizer object.
  3. A pattern that marks the end of the grammar. If this is a string it is converted
     to an exact Pattern object.

  When the end grammar pattern occurs, then the grammar returns to the grammar
  that was active before the new grammar started. Thus, nested grammars are
  supported.

  The third item is optional. If not specified, the :class:`Tokenizer` will not exit the
  new grammar and return to the parent grammar.
  """

  # ----------------------------------------------------------------------------
  def __init__(self, name, *patterns):
    self.name     = name
    self.patterns = []
    for pattern in patterns:
      if isinstance(pattern, (tuple, list)):
        self.addPattern(*pattern)
      else:
        self.addPattern(pattern)

  # ----------------------------------------------------------------------------
  def addPattern(self, pattern, new_grammar=None, end_grammar=None):
    """
    Add a pattern as part of the grammar. Note that the order of the patterns is
    important.

    :param pattern: A pattern that is part of the grammar. If a string is passed in,
           it is converted to an exact pattern.
    :param state: An optional grammar to switch to.
    :param endstate: Pattern that marks the end of the new grammar. If a string is
           passed in, it is converted to an exact pattern.
    """
    from six import string_types
    from .PyPE import P
    asPtn = lambda val: P(val) if isinstance(val, string_types) else val
    pattern, end_grammar = asPtn(pattern), asPtn(end_grammar)

    if not isinstance(pattern, Pattern):
      raise Exception("Items included in a Grammar must be Pattern objects")
    if len([item is None for item in (new_grammar, end_grammar)]) == 1:
      raise Exception("For a Grammar, a new grammar and the end rule for the grammar must be specified together")
    if end_grammar is not None:
      if not isinstance(end_grammar, Pattern):
        raise Exception("The end grammar pattern must be a Pattern object")
    self.patterns.append( (pattern, new_grammar, end_grammar) )

  # ----------------------------------------------------------------------------
  def debug(self, debugOpt, token=None):
    """
    Set the debug option for a pattern in this Grammar.

    :param debugOpt: The debug option to pass to the pattern debug function.
    :param token: The token to set debug options for. If this is None, the debug
           option is set for all the tokens.
    """
    for pattern, dummy, dummy in self.patterns:
      if token is not None and token != pattern.name: continue
      pattern.debug(debugOpt)

  # ----------------------------------------------------------------------------
  def __getitem__(self, item):
    return self.patterns[item]

  # ----------------------------------------------------------------------------
  def __len__(self):
    return len(self.patterns)

  # ----------------------------------------------------------------------------
  def __repr__(self):
    return "Grammar({0})".format(self.name)

# ==============================================================================

class Tokenizer(object):
  """
  A :class:`Tokenizer` is used to parse text and break the text into tokens using grammars.
  The :class:`Tokenizer` is initialized with one or more named grammars, and a root grammar
  is specified.
  """

  # ----------------------------------------------------------------------------
  def __init__(self, initial_grammar = "root", end_grammar = None, **grammars):
    """
    Initialize the Tokenizer. Grammars are passed as keyword arguments to the
    Tokenizer constructor. A 'root' grammar must be passed to the constructor,
    or the 'initial_grammar' must be specified as one of the grammars that are
    passed to the constructor.

    :param initial_grammar: This indicates which grammar is root grammar. By
           default, the grammar named 'root' is the root grammar.
    :param end_grammar: If the root grammar has a pattern that ends parsing, it
           is specified via this parameter.
    :param \**grammars: All keyword arguments passed to the Tokenizer
           constructor are considered to be grammars. The grammar should contain
           an ordered list or tuple with the rules that make up the grammar. See
           :func:`__addGrammar__` for more details about the grammar rules list.
           A :class:`Grammar` object is created for each grammar item that is
           specified.
    """
    self.initial_grammar = initial_grammar
    # grammar stack - indicate which grammar we are in and the end grammar marker
    self.stack = []
    self.grammars = {}
    self._debug_ = False

    for name, grammar in grammars.items():
      self.__addGrammar__(name, grammar)

    # Set the initial grammar
    self.__setGrammar__(initial_grammar, end_grammar)

  # ----------------------------------------------------------------------------
  def __addGrammar__(self, name, rules):
    """
    Add a grammar to the list of grammars for this tokenizer. Each grammar has
    a name and an ordered set of rules that define the tokens associated with
    the grammar.

    :param name: The name of the grammar.
    :param rules: The set of rules associated with the grammar. This is a list
           or tuple that contains an ordered set of patterns that define what
           the grammar is looking for. Each pattern needs to be named, and when
           getTokens is found, and a grammar is active, and a pattern match is
           found for one of the tokens, the name of the pattern is returned as
           the token name along with the pattern match.
    """
    # TODO: Check if tokens is a list and verify that the entries are properly formed.
    self.grammars[name] = Grammar(name, *rules)

  # ----------------------------------------------------------------------------
  def debug(self, enable):
    self._debug_ = enable

  # ----------------------------------------------------------------------------
  def __setGrammar__(self, name, end_grammar):
    """
    Add a grammar to the top of the grammar stack. The rule at the top of the
    stack is active until the end_grammar rule is matched.

    :param name: The name of the new grammar to use. Must be one of the
           registered grammars.
    :param end_grammar: The pattern for ending the grammar. Note that this must
           be a named Pattern.
    """

    if self._debug_:
      print("Entering Grammar: %s" % name)

    if name not in self.grammars:
      raise Exception("No grammar named '{0}' has been register for Tokenizer".format(name))

    grammar = self.grammars[name] # The grammar rules
    self.stack.append({'name': name, 'grammar':grammar, 'end grammar':end_grammar})

  # ----------------------------------------------------------------------------
  def currentGrammarName(self):
    """
    :return: The name of the active grammar.
    """
    if len(self.stack) == 0: return None
    return self.stack[-1]['name']

  # ----------------------------------------------------------------------------
  def getTokens(self, string, index=0):
    """
    Apply the tokenizer to the given string starting at the specified index and
    return the tokens that are found in pairs (token name, match object). The
    token name is the name associated with the token Pattern in the grammar
    rules list. This is an iterator function.

    :param string: The string to tokenize.
    :param index: The location in the string to start (default 0)
    """
    from .PyPE import Match
    if not isinstance(string, BackCaptureString): string = BackCaptureString(string)

    while True:
      grammar, end_grammar = [self.stack[-1][item] for item in ('grammar','end grammar')]

      # ------------------------------------------------------------------------
      # See if the grammar has ended first. If so, pop a grammar from the stack
      # and continue.
      # ------------------------------------------------------------------------
      if end_grammar is not None:
        match = end_grammar.match(string, index)
        if isinstance(match, Match):
          if end_grammar.name is not None: yield (end_grammar.name, match)
          index = match.end
          # Pop a grammar from the stack
          if self._debug_:
            print("Exiting Grammar: %s" % self.stack[-1]['name'])
          self.stack.pop()
          continue # reset loop

      # ------------------------------------------------------------------------
      # Loop through the grammar patterns to find a match.
      # ------------------------------------------------------------------------
      for pattern, new_grammar, end_new_grammar in grammar:
        name = pattern.name
        match = pattern.match(string, index)
        if isinstance(match, Match):
          if name is not None: yield (name, match)

          # TODO: Check if the new_grammar is the same as the current grammar. If so, raise exception
          if new_grammar is None and index == match.end:
            raise StopIteration() # No Progress
          index = match.end

          # --------------------------------------------------------------------
          # If this match starts a new grammar, add the grammar to the stack.
          # --------------------------------------------------------------------
          if new_grammar is not None:
            self.__setGrammar__(new_grammar, end_new_grammar)
          break
      else:
        return
        #raise StopIteration()
