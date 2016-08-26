from PyLPEG import P, S, C, Cc, Cg, Col, whitespace, whitespace0 as ws, \
     newline, matchUntil, SOL
from Tokenizer import Tokenizer

whitespace.debug(False)

# ==============================================================================
# Template Class
# ==============================================================================

class Template(object):
  startPyTag  = P("@[")     # Start python code block
  endPyTag    = P("]@")     # End python code block
  trimWS      = P("^")      # Symbol to trim whitespace
  brk = "# =============================================================================="

  templateDir = "temp"

  # Escape the double quote character (") and slash character in TEXT to be written out.
  escapeDblQuoteAndEscChr = (C(1 - S('"\\')) *
                             (P('"') * Cc('\\"') + P('\\')*Cc('\\\\') + P(0)))**0

  # ----------------------------------------------------------------------------
  def __init__(self, filename, readFile=True, base_function="function"):
    """

    :param filename: The filename to use for the template. When readFile is true,
                     this should be the name of the file being read. The name of
                     the python file that is generated in the templateDir is
                     the base name from the filename plus '.py' if not already the
                     file extension.
    :param readFile: Indicate if the source should be read from the given file.
    :param base_function: The base name to use for auto generated function names.
    """
    from os.path import basename

    if filename is None:
      raise ValueError("The filename must be specified for a Template")

    self.templatename    = basename(filename if filename.endswith("*.py") else filename + ".py")
    self.base_function   = base_function # Base name to use for generated functions
    self.function_num    = 0
    self.code_blocks     = []
    self.function_names  = []
    self.isCodeGenerated = False

    if readFile:
      with open(filename, "rb") as file:
        src = file.read()
      self.addPythonFunction(src)

  # ----------------------------------------------------------------------------
  def __textParser__(self):
    """
    Define the parser that gets the text between python tags. Trim whitespace
    where python tag indicates newline and whitespace is stripped (i.e., @[^).
    Read text up to python tag marker or end of string.

    :return: Text parse rule.
    """
    startPyTag = self.startPyTag
    trimWS     = self.trimWS


    oneLine     = 'one line'   | matchUntil(newline + startPyTag)
    maybeTrimWS = 'maybe trim' | ((newline + SOL())*ws)**-1*(-(startPyTag*trimWS))
    ifTrimWS    = 'ifTrimWS'   | ((newline + SOL())*ws)**-1
    #maybeTrimWS = 'maybe trim' | ((SOL() + newline)*ws)**-1*(-(startPyTag*trimWS))
    #ifTrimWS    = 'ifTrimWS'   | ((SOL() + newline)*ws)**-1

    TEXT = Cc("TEXT") * ~P(1) * C((maybeTrimWS*oneLine)**0) * ifTrimWS
    TEXT = "TEXT" | TEXT / self.__processTextMatch__
    return TEXT

  # ----------------------------------------------------------------------------
  def __processTextMatch__(self, match):
    from PyLPEG import quote

    text = match.captures[1]
    escaped_text = "".join(self.escapeDblQuoteAndEscChr(text).captures)
    if escaped_text == "":
      return match.setCaptures([])

    pycode = PyCodeBlock(['write("""{0}""")'.format(escaped_text)])
    return match.setCaptures(pycode)

  # ----------------------------------------------------------------------------
  def __pyTagParser__(self):
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
    * *write*: Flag that is stored if '=' option is specified.
    * *right align*: Flag that is stored if '>' option is specified.
    * *left align*: Flag that is stored if '<' option is specified.
    * *unindent*: Colons to mark levels of unindentation based on number of
      colons. No whitespace between colons is allowed.
    * *initial code*: The first line of code that resides on the line with
      python tag '@['. If no code is on the line this is excluded.
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

    # ---- End Block identifiers (colons) ----
    unindent = (Prp("unindent",C(P(":")**1))*ws + P(True))

    # ---- Code Lines ----
    empty  = Prp("empty line", ws*newline)
    Ccode  = C((1-(newline + end)&'hide')**1)        # Capture code
    code   = Prp("code", C(ws)*Ccode) * newline**-1
    code_line = empty + code + ws

    # ---- First Line of Code ----
    initial_code = (Prp("initial code", Ccode) - newline) + P(True)

    # --------------------------------------------------------------------------
    # PYTAG parts
    # --------------------------------------------------------------------------

    PYTAG = Cc("PYTAG") * \
            (start * options * unindent * initial_code * code_line**0 * end)
    PYTAG = "PYTAG" | PYTAG / self.__processPyTagMatch__
    return PYTAG

  # ----------------------------------------------------------------------------
  def __processPyTagMatch__(self, match):
    """
    Convert data structures returned by the PEG into a PyCodeBlock object. Set
    correct indents, and calculate the number of indents included in src block.

    :param match: The match from the PYTAG pattern.
    :return: A PyCodeBlock object
    """

    code_lines   = []    # The processed lines of code
    indent_stack = []    # Store the indent whitespace
    state = {
      'option'        : None,  # Write option
      'start_indent'  : 0,     # Location just before the pyTag start marker '@['
      'end_indent'    : 0,     # Location just after the pyTag end marker ']@'
      'unindentLvl'   : 0,     # Indicate the number of unindent levels before this code block
      'new block'     : False, # Marks the start of a new block
      'hasError'      : False, # Mark that an error occurred.
    }

    # Check if an exta indent was added due to block indent on first line following '@['
    hasExtraFirstLineIndent = lambda: len(indent_stack[0][1]) > 0
    # Get the indent level to get the unmodified indent from the raw file
    baseIndentIndex = lambda: 1 if hasExtraFirstLineIndent() else 0

    # indent_stack first index mnemonic parameters
    bottom_of_stack = 0  # The bottom of the stack (get base indent)
    top_of_stack    = -1 # Get the top item on the indent stack

    # indent_stack second index mnemonic parameters
    raw_indent  = 0      # Index of the string that gives the unmodified indent.
    code_indent = 1      # Index of the string that gives the modified indent.

    # --------------------------------------------------------------------------
    def stripBaseWhitespace(indent):
      # TODO: report an error if indent_stack is size 0 after first call?
      if len(indent_stack)-1 < baseIndentIndex():
        return indent

      base = indent_stack[baseIndentIndex()][raw_indent]
      base_sz = len(base)
      if len(indent) < base_sz:
        # TODO: indicate an error that code is not indented consistently.
        state['hasError'] = True
        return ''
      if not indent.startswith(base):
        # TODO: report a warning that spaces and tabs are not consistent.
        pass
      return indent[base_sz:]

    # --------------------------------------------------------------------------
    def add2indentStack(indent):
      state['new block'] = False

      # If the first line of code starts a block (ends with colon) extra indent
      # is added. This is stored in indent_stack[0][1].
      extra_indent = '' if len(indent_stack) == 0 else indent_stack[bottom_of_stack][code_indent]
      szStack = len(indent_stack)

      if szStack == 0 or hasExtraFirstLineIndent() and szStack == 1:
        # Add the base indent
        indent_stack.append((indent,extra_indent))
      elif len(indent) < len(indent_stack[top_of_stack][raw_indent]):
        #TODO: report error that block code is not indented
        state['hasError'] = True
        indent_stack.append((indent, extra_indent+stripBaseWhitespace(indent)))
      elif not indent.startswith(indent_stack[top_of_stack][raw_indent]):
        #TODO: Report inconsistent tabs and spaces.
        # Add indent from parent indent plus extra characters from this indent
        idt = indent_stack[-1][1] + indent[len(indent_stack[top_of_stack][raw_indent]):]
        indent_stack.append((indent, extra_indent+idt))
      else:
        indent_stack.append((indent, extra_indent+stripBaseWhitespace(indent)))

    # --------------------------------------------------------------------------
    def adjustIndent(indent):
      """
      Set the indent to the correct size for the final code.

      :param indent: The actual indentation in the source file
      :return: The modified indentation that removed the base indent and
               possibly adds an extra indent (if first line starts a block).
      """

      # The following should just occur for the first line. If we have no
      # indentation yet, return an empty string
      if len(indent_stack) == 0: return ''

      sz = len(indent_stack)
      for i in xrange(sz-1, -1, -1):
        unmodified_indent, modified_indent = indent_stack[i]
        if indent == unmodified_indent: return modified_indent
        indent_sz, unmodified_sz = (len(indent), len(unmodified_indent))
        # TODO: Report inconsistent tabs and spaces
        if indent_sz == unmodified_sz: return modified_indent
        # TODO: Report an error indent does not match a current indent level.
        if indent_sz > unmodified_sz: return modified_indent
        # Suggests that code is being unindented
        # indent_sz < unmodified_sz
        if i > baseIndentIndex():
          indent_stack.pop()
        else:
          # hasExtraFirstLineIndent indicates that the first line after '@[' had
          # code with a ':' at end. Thus a dummy indent was added for this first
          # block of code.
          if hasExtraFirstLineIndent():
            indent_stack.pop()      # Remove the indent from the line just after '@['
            indent_stack.pop()      # Remove the extra indent that was added at top of stack
            add2indentStack(indent) # Add the indent associate with the current line of code
            return indent_stack[baseIndentIndex()][1]

          # TODO: Report that the indent is smaller than the base indent
          return indent_stack[baseIndentIndex()][1]

    # --------------------------------------------------------------------------
    def addCodeAndCheckForColon(indent, code):
      if state['new block']: add2indentStack(indent)
      code = code.strip()             # Get rid of trailing whitespace
      # Add indentation
      indent = adjustIndent(indent)
      code_lines.append(indent + code)
      if code.startswith('#'): return # Comment line - no need to look for colons

      # Do we want a more sophisticated way to detect valid colons at end of line?
      if code.endswith(':'): state['new block'] = True

    # --------------------------------------------------------------------------

    for capture in match.captures:
      cmd = capture[0]

      # ['start indent', column] - Column before pyTag start marker '@['
      if cmd == "start indent":
        state['start_indent'] = capture[1]
        continue

      # ['end indent', column] - Column after pyTag end marker ']@'
      if cmd == "end indent":
        state['end_indent'] = capture[1]    # Column where the PyTag ended
        continue

      # ['write']
      if cmd == "write":
        state['option'] = 'write'
        # TODO: Finish the write processing
        continue

      # ['right align']
      if cmd == "right align":
        state['option'] = 'right align'
        # TODO: Finish the right align processing
        continue

      # ['left align']
      if cmd == "left align":
        state['option'] = 'left align'
        # TODO: Finish the left align processing
        continue

      # ['unindent', '::'] - Number of unindents (number of colons)
      if cmd == 'unindent':
        state['unindentLvl'] = len(capture[1])
        continue

      # ['empty line'] - An empty line of code
      if cmd == "empty line":
        code_lines.append("")
        continue

      # ['initial code', '<code>'] - The code on the same line with '@['
      if cmd == 'initial code':
        addCodeAndCheckForColon('', capture[1])

        # Add a base indent if the first python line ends with a colon.
        if state['new block']: indent_stack.append(('','  '))
        continue

      # ['code', '<indent>', '<src code>']
      if cmd == "code":
        # Code from the line following pyTag marker '@['
        indent, code = capture[1:3]
        addCodeAndCheckForColon(indent, code)
        continue

    # --------------------------------------------------------------------------
    # Handle the write options.
    # --------------------------------------------------------------------------

    write_option = state['option']
    indentLvl = max(len(indent_stack)-1, 0)
    if write_option is not None:
      if indentLvl != 0:
        # TODO: Report an error. A write command cannot be used with a series of comamnds.
        pass
      elif write_option == "write":
        if len(code_lines) == 1:
          code_lines[0] = 'write({0})'.format(code_lines[0].strip())
        else:
          code_lines.insert(0, "write(")
          code_lines.append(")")
      else:
        width = max(state['end_indent'] - state['start_indent'],0)
        align = "<" if write_option == "left align" else ">"
        if len(code_lines) ==1:
          code_lines[0] = "write('{{0:{0}{1}}}'.format({2}))".format(align, width, code_lines[0].strip())
        else:
          code_lines.insert(0, "write('{{0:{0}{1}}}'.format(".format(align, width))
          code_lines.append("))")

    # --------------------------------------------------------------------------
    # Set the PyCodeBlock as the .
    # --------------------------------------------------------------------------

    pycode = PyCodeBlock(code_lines,
                         unindent_before = state['unindentLvl'],
                         indent_after    = indentLvl)
    return match.setCaptures([pycode])

  # ----------------------------------------------------------------------------
  def __getFunctionName__(self, function_name=None):
    if function_name is not None:
      self.function_names.append(function_name)
      return function_name

    self.function_num += 1
    function_name = self.base_function + str(self.function_num)
    self.function_names.append(function_name)
    return function_name

  # ----------------------------------------------------------------------------
  def __addCodeBlock__(self, pycodeblock):
    self.code_blocks.append(pycodeblock)

  # ----------------------------------------------------------------------------
  def addPythonFunction(self, src, function_name=None):
    T = Tokenizer(root = (self.__pyTagParser__(), self.__textParser__()))

    code = ["", self.brk,
            "def {0}():".format(self.__getFunctionName__(function_name))]
    pcb = PyCodeBlock(code, indent_after=1)
    self.__addCodeBlock__(pcb)

    for token, match in T.getTokens(src):
      if match.hasCaptures(): self.__addCodeBlock__(match.getCapture(0))

    self.__addCodeBlock__("set indent to 0")

  # ----------------------------------------------------------------------------
  def __generateCode__(self):
    from os.path import join

    header = [self.brk,
              'def __moduleParams__(params):',
              '  import sys',
              '  module = sys.modules[__name__]',
              '  for param, value in params.items():',
              '    setattr(module, param, value)']
    self.code_blocks.insert(0, PyCodeBlock(header))

    with open(join(self.templateDir, self.templatename), "wb") as file:
      indent = 0
      for pycodeblock in self.code_blocks:
        if pycodeblock == "set indent to 0":
          indent = 0
          continue

        indent -= pycodeblock.unindent_before
        # TODO: report an error
        if indent < 0:
          raise Exception("The generated python code specified too many unindents")
        file.write(pycodeblock.getSource(indent))
        indent += pycodeblock.indent_after

    self.isCodeGenerated = True

  # ----------------------------------------------------------------------------
  def render(self, parameters={}, function=None, stack=None):
    function = function or self.function_names[0]

    if not self.isCodeGenerated: self.__generateCode__()
    modulename = self.templatename[:-3]
    module = getattr(__import__(self.templateDir, fromlist=[modulename]), modulename)

    stack1 = stack or Stack()

    module.__moduleParams__(parameters)
    module.__moduleParams__({'write':stack1.write})

    fn = getattr(module, function)
    fn()

    if stack is None:
      return stack1.toString()

# ==============================================================================
# PyCodeBlock Class
# ==============================================================================

class PyCodeBlock(object):
  indent = "  " # The whitespace used for an indent

  # ----------------------------------------------------------------------------
  def __init__(self, lines_of_code, unindent_before=0, indent_after=0):
    self.lines_of_code   = lines_of_code
    self.unindent_before = unindent_before
    self.indent_after    = indent_after

  # ----------------------------------------------------------------------------
  def getSource(self, indent=0):
    # TODO: Indicate the source location
    indt = self.indent * indent
    return "\n".join([indt + line for line in self.lines_of_code]) + "\n"

  # ----------------------------------------------------------------------------
  def __repr__(self):
    return "\n".join(self.lines_of_code)

# ==============================================================================
# Stack class
# ==============================================================================

class Stack(object):
  """
  Stack that holds the values written from Template
  """

  # ----------------------------------------------------------------------------
  def __init__(self):
    self.stack = []

  # ----------------------------------------------------------------------------
  def write(self, line):
    self.stack.append(line)

  # ----------------------------------------------------------------------------

  def toString(self):
    from StringIO import StringIO
    stack = self.stack
    self.stack = []

    output = StringIO()
    for line in stack:
      if callable(line):
        value = line()
        # If any items were added to the new stack, get those values.
        stackstuff = self.toString()
        output.write(stackstuff)
        if value is not None:
          output.write(str(value))
      else:
        output.write(line)

    return output.getvalue()

# ==============================================================================


src = r"""
    "This is a test"
    @[ if name == "fred":
          write(name)
          write("done")
    ]@
    @[: a = "testing"
       bob = 5
       q=7
      ^]@
    @[^= bob  ]@

    @[^>"this is a test"^]@
    "Stuff
"""
#from Template import Template

t = Template("Temp", False)
t.addPythonFunction(src)
t.addPythonFunction(src)
print t.render({'name':"fred",'a':"A Value"})