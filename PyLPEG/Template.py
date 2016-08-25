from PyLPEG import P, C, Cc, Cg, Col, whitespace, whitespace0 as ws, newline, \
  matchUntil
from Tokenizer import Tokenizer

whitespace.debug(False)

# ==============================================================================
# Template Class
# ==============================================================================

class Template(object):
  startPyTag = P("@[")     # Start python code block
  endPyTag   = P("]@")     # End python code block
  trimWS    = P("^")      # Symbol to trim whitespace

  # ----------------------------------------------------------------------------
  def __init__(self, src):
    self.src = src

  # ----------------------------------------------------------------------------
  def textParser(self):
    """
    Define the parser that gets the text between python tags. Trim whitespace
    where python tag indicates newline and whitespace is stripped (i.e., @[^).
    Read text up to python tag marker or end of string.

    :return: Text parse rule.
    """
    startPyTag = self.startPyTag
    trimWS     = self.trimWS

    oneLine     = 'one line' | matchUntil(newline + startPyTag)
    maybeTrimWS = 'maybe trim' | (newline*ws)**-1*(-(startPyTag*trimWS))
    ifTrimWS    = 'ifTrimWS' | (newline*ws)**-1

    TEXT = "TEXT" | Cc("TEXT") * ~P(1) * C((maybeTrimWS*oneLine)**0) * ifTrimWS
    return TEXT

  # ----------------------------------------------------------------------------
  def pyTagParse(self):
    """
    Define the parser for python tags @[...]@. The format of the python tag is:

       @[(^)(=|>|<)(:) <code> (^)]@

    The values in parenthesis are optional and parenthesis should not be
    included. No whitespace is allowed between the python tag '@[' and '^' and
    '=', '>', or '<'. Similarly, no whitespace is allowed between '^' and the
    close tag marker ']@'.

      * *^* indicates whitespace and newline should be removed at start or end of
        block.
      * *=|>|<* indicates that only one of these options is allowed.
      * *=* indicates that the code result should be written to the file.
      * *>* indicates that the column range (size) of the tag should be preserved
        in the text if possible, and the text should be right aligned.
      * *<* indicates that the column range (size) of the tag should be preserved
        in the text if possible, and the text should be left aligned.
      * *:* after the options indicates the end of a block. Zero or more colons
        may be included to indicate multitple unindents. Whitespace is allowed
        before colons, but not between colons.
      * *<code>* is the python code for the tag.
      *

    Information is gathered to allow the source code to be formatted properly,
    and to detect the number of block indents in the code. Block unindents are
    marked by colons at the start of the block. The following data should be
    stored in captures. Each captured value should be contained in a capture
    group, with the name from the list below included with the capture.

    * *start indent*: The indent before the start python tag.
    * *initial indent*: The column number (Col) or indent where the code starts
       on the same line as the python tag '@['. If there is no code on the same
       line as the python tag, this value should be excluded.
    * *initial index*: The string index (Cp) at the location where the code
      starts on the same line as the python tag. If there is no code on the same
      line as the python tag, this value should be excluded.
    * *code*: The line of code as whitespace and code as separate captures.
    * *empty line*: Empty line of code
    * *end indent*: The indent after the close python tag.

    :return: Python Tag parse rule.
    """

    startPyTag = self.startPyTag
    endPyTag   = self.endPyTag
    trimWS     = self.trimWS

    # Options are specified without a value in a capture group
    Opt = lambda cmd: Cg(Cc(cmd))

    # Properties are specified with a name and include any captures in the
    # provided pattern
    Prp = lambda name, pattern: Cg(Cc(name)*pattern)

    # --------------------------------------------------------------------------
    # PYTAG parts
    # --------------------------------------------------------------------------

    # ---- Options ----
    wrt = "=" * Opt("write")                    # Write to stack flag
    ral = ">" * Opt("right align")              # Right align flag
    lal = "<" * Opt("left align")               # Left align flag
    options = (wrt + ral + lal)**-1 * ws

    # ---- Python tag range ----
    start_indent = Prp("start indent",Col())
    end_indent   = Prp("end indent",Col())

    # ---- end tag parts ----
    rmWSnewline = ws*newline + P(True) # Only remove is ws followed by newline
    endTrimWS = trimWS*endPyTag*end_indent*rmWSnewline
    endNoTrim = endPyTag*end_indent

    # ---- Start and end pytag ----
    start = start_indent * startPyTag * trimWS**-1
    end   = endTrimWS + endNoTrim

    # ---- Code Lines ----
    empty  = Prp("empty line", ws*newline)
    code   = Prp("code", C(ws)*C((1-(newline + end)&'hide')**1)) * newline**-1
    code_line = empty + code + ws

    # ---- First Line of Code ----
    initial_indent = (Prp("initial indent", Col()) - newline) + P(True)
    initial_code   = code + P(True)

    # --------------------------------------------------------------------------
    # PYTAG parts
    # --------------------------------------------------------------------------

    PYTAG = "PYTAG" | Cc("PYTAG") * \
        start * options * initial_indent * initial_code * code_line**0 * end
    return PYTAG

  # ----------------------------------------------------------------------------
  def generateCode(self):
    T = Tokenizer(root = (self.pyTagParse(),self.textParser()))

    for token, match in T.getTokens(self.src):
      print
      print(token)
      print(match.captures)

  # ----------------------------------------------------------------------------
  def render(self, parameters=None):
    pass

# ==============================================================================


src = """
    This is a test
    @[^ :: elif asdf and
          asdfn and adfn: ]@
    @[^
       a = src.select(block="test")
       bob = 5
          more stuff

      ^]@
@[  bob  ]@

    @[^ :: else : ]@
    Stuff
"""

t = Template(src)
t.generateCode()