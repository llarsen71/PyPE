def removeSrcIndent(pysrc):
  """
  .. function: removeSrcIndent(pysrc)

  This function takes a block of text (presumably python source code) and
  removes the base indent from the text. The base indent is the amount of
  whitespace on the first line. If any lines (that contain text) are indented
  less than the first line, an error occurs.

  :param pysrc: A string containing python source code.
  :return: The source code with the base indent removed.
  """
  from PyLPEG import whitespace0 as ws, Col, P, C, Cg, Cp, newline as nl, EOL, \
       Match
  from StringIO import StringIO

  # TODO: pass in the line number and report errors

  # ----------------------------------------------------------------------------
  # Get the indent from the first line of code (ignore blank lines at the start)
  # ----------------------------------------------------------------------------

  # Store the indent characters to make sure that they are consistent with
  # whitespace on each src lines. If they do no match an error will be reported.

  getIndent = (ws*nl)**0 * C(ws) * Col()
  whitespaceChrs, indent = getIndent(pysrc).captures

  # ----------------------------------------------------------------------------
  # Based on the indent of the first line, remove the indent from each line.
  # ----------------------------------------------------------------------------

  # 1. Split into indent characters (based on number of whitespace characters
  #    on first line of code) and the rest of the line.

  initialIndent = P(1 - nl) ** -indent
  restOfLine    = ('hide' & 1 - nl) ** 0 * (nl)**-1

  splitLines = Cg(Cp() * C(initialIndent) * C(restOfLine))**0

  # Write the unindented code to a string buffer
  code = StringIO()
  match = splitLines(pysrc)

  isBlank      = ws * EOL()       # Check for no source code on line
  isWhitespace = lambda spaces: isinstance(isBlank(spaces), Match)
  hasCode      = lambda src: isBlank(src) == None

  # 2. For each line, check that the first characters really are whitespace. If
  #    not,
  for location, spaces, src in splitLines(pysrc):
    if not isWhitespace(spaces):
      raise Exception("The embedded python source code contains illegal "
                      "indentation")
    if hasCode(src) and spaces != whitespaceChrs:
      raise Exception("Illegal mixture of tabs and spaces")
    code.write(src)

  return code.getvalue()

def parseSrc(src):
  """
  Parse the source file and return the parsed data.

  :return:  Parsed data
  """
  from PyLPEG import P, R, S, C, Cc, Cg, Col, whitespace, \
       whitespace0, newline, SOL
  from Tokenizer import Tokenizer

  scode = P("@[")     # Start python code block
  ecode = P("]@")     # End python code block

  ws = whitespace0 & 'hide'
  nl = newline

  # For an option, group the option name into an array
  Opt = lambda cmd: Cg(Cc(cmd))

  # Remove whitespace flag. Indicate where to remove whitespace (start or end)
  rws = lambda where: ("^" * Cg(Cc("remove ws")*Cc(where)))**-1

  # ----------------------------------------------------------------------------
  # PYTAG Options
  # ----------------------------------------------------------------------------
  wrt = ws * "=" * Opt("write")                    # Write to stack flag
  ral = ws * ">" * Opt("right align")              # Right align flag
  lal = ws * "<" * Opt("left align")               # Left align flag

  options = (wrt + ral + lal + P(0))

  # ----------------------------------------------------------------------------
  # Other
  # ----------------------------------------------------------------------------

  # Indent the first line of python source code over to where it is in the
  # template file.
  def srcindent(match, indicateIfIsBlock=False):
    firstLineColumn, pysrc = match.captures
    srcHasNewline = pysrc.find("\r") >= 0  or pysrc.find("\n") >= 0
    if srcHasNewline:
      pysrc = removeSrcIndent(" "*int(firstLineColumn) + pysrc.rstrip())
    else:
      pysrc = pysrc.strip()
    match.captures = [["python", pysrc]]

    isBlock = False
    if pysrc.endswith(":"):
      match.addCapture(["start block"])
      isBlock = True
    return isBlock if indicateIfIsBlock else match

  # ----------------------------------------------------------------------------

  pysrc = ('hide' & 1 - P("^")**-1 * ecode)**0

  # ----------------------------------------------------------------------------

  # Count number of colons and add a capture to get unindent levels.
  def getNumUnindents(match):
    match.captures = [len(match.captures)]
    return match

  # ----------------------------------------------------------------------------

  numUnindents = Cg(Cc("unindent") * (('hide' & ws*C(":"))**1/getNumUnindents) * ws)    # End block

  # ----------------------------------------------------------------------------

  def isBlock(match):
    """
    Check whether the code ends with a ':'. This indicates start of a code block.
    """

    # We haven't determined whether this has source code, but assume it does at
    # first and prepare the source code.
    is_block = srcindent(match, indicateIfIsBlock=True)
    if not is_block: match.captures = []
    return match

  # ----------------------------------------------------------------------------
  # TAGS
  # ----------------------------------------------------------------------------

  # Only allow one line - TODO: check for multiple lines and print error
  ENDBLK = "END BLOCK" | Cc("END BLOCK") * scode * rws("start") * numUnindents * \
                         (Col() * C(('hide' & 1-P("^")**-1*ecode)**0)/isBlock) * \
                         rws("end")**-1 * ecode

  PYTAG  = "PYTAG"     | Cc("PYTAG") * scode * rws("start") * options * \
                         ((Col() * C(pysrc)) / srcindent) * \
                         rws("end") * ecode

  TEXT   = "TEXT"      | Cc("TEXT") * C(('hide' & 1 - scode)**1)

  #PYTAG.debug(True)
  #ENDBLK.debug(True)

  T = Tokenizer(root=(ENDBLK, PYTAG, TEXT))
  for name, match in T.getTokens(src):
    print name
    print match.captures

# ==============================================================================
# Template Class
# ==============================================================================

class Template(object):
  def __init__(self, src):
    self.src = src

  def generateCode(self):
    pass

  def render(self, parameters=None):
    pass

src = """
    This is a test
    @[ :: elif asdf and
          asdfn and adfn: ]@
    @[^ a = src.select(block="test")
          bob = 5
          more stuff
      ^]@@[  bob  ]@

    @[^ :: else : ]@
    Stuff
"""

parseSrc(src)
#removeSrcIndent(src)