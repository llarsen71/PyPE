from PyLPEG import Pattern, BackCaptureString
# ==============================================================================

class Grammar(object):

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

    :param pattern: A pattern that is part of the grammar
    :param state: An optional grammar to switch to.
    :param endstate: Pattern that marks the end of the new grammar.
    """

    if not isinstance(pattern, Pattern):
      raise Exception("Items included in a Grammar must be Pattern objects")
    if pattern.name is None:
      raise Exception("Patterns included in a Grammar must include a name")
    if len([item is None for item in (new_grammar, end_grammar)]) == 1:
      raise Exception("For a Grammar, a new grammar and the end rule for the grammar must be specified together")
    if end_grammar is not None:
      if not isinstance(end_grammar, Pattern):
        raise Exception("The end grammar pattern must be a Pattern object")
      if end_grammar.name is None:
        raise Exception("The end grammar pattern must have a name")
    self.patterns.append( (pattern, new_grammar, end_grammar) )

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

  # ----------------------------------------------------------------------------
  def __init__(self, initial_grammar = "root", end_grammer = None, **grammars):
    self.initial_grammar = initial_grammar
    # grammar stack - indicate which grammar we are in and the end grammer marker
    self.stack = []
    self.grammars = {}

    for name, grammar in grammars.items():
      self.addGrammar(name, token)

    # Set the initial grammar
    self.__setGrammar__(self.grammars[initial_gramar], end_grammer)

  # ----------------------------------------------------------------------------
  def __setGrammar__(self, grammar, end_grammar):
    """

    :param grammar: The grammar added to the stack
    :param end_grammar: The pattern for ending the grammar
    """
    self.stack.append({'grammar':grammar, 'end grammar':end_grammar})

  # ----------------------------------------------------------------------------
  def addGrammar(self, name, grammar):
    # TODO: Check if tokens is a list and verify that the entries are properly formed.
    self.grammars[name] = Grammar(name, *grammar)

  # ----------------------------------------------------------------------------
  def getTokens(self, string, index=0):
    """
    """
    #if not isinstance(string, BackCaptureString):
    #  string = BackCaptureString(string)

    while True:
      grammar, end_grammar = self.stack[-1]

      # ------------------------------------------------------------------------
      # See if the grammar has ended first. If so, pop a grammar from the stack
      # and continue.
      # ------------------------------------------------------------------------
      if end_grammar is not None:
        match = end_grammar.match(string, index)
        if isinstance(match, Match):
          yield (end_grammar.name, match)
          # Pop a grammar from the stack
          self.grammars.pop()
          continue # reset loop

      # ------------------------------------------------------------------------
      # Loop through the grammar patterns to find a match.
      # ------------------------------------------------------------------------
      for pattern, new_grammar, end_new_grammar in grammar:
        name = pattern.name
        match = pattern.match(string, index)
        if isinstance(match, Match):
          yield (name, match)

          # TODO: Check if the new_grammar is the same as the current grammar. If so, raise exception
          if new_grammar is None and index == match.end: raise StopIteration() # No Progress
          index = match.end

          # --------------------------------------------------------------------
          # If this match starts a new grammar, add the grammar to the stack.
          # --------------------------------------------------------------------
          if new_grammar is not None:
            self.__setGrammar__(self.grammars[new_grammar], end_new_grammar)
          break
      else:
        raise StopIteration()