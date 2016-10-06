from PyPE import P, S, R, C, Cc, Cb, Cg, Cs, SOL, EOL, alpha, digit, newline, \
                 quote, V, setVs, Sc, Sp, Sm, Ssz, matchUntil, whitespace

import sys
sys.setrecursionlimit(10000)

# ==============================================================================
def NUMBER_():
  # ----------------------------------------------------------------------------
  # INTEGER and LONGINTEGER definition
  # ----------------------------------------------------------------------------
  hexdigit       = digit + R("af","AF")
  bindigit       = S("01")
  octdigit       = R("07")
  nonzerodigit   = R("19")

  decimalinteger = (nonzerodigit * digit**0) + P("0")
  octinteger     = "0" * S("oO") * octdigit**1  + "0" * octdigit**1
  hexinteger     = "0" * S("xX") * hexdigit**1
  bininteger     = "0" * S("bB") * bindigit**1

  integer        = decimalinteger + octinteger + hexinteger + bininteger  & 'hide'
  longinteger    = integer * S("lL")  & 'hide'

  # ----------------------------------------------------------------------------
  # floating point numbers
  # ----------------------------------------------------------------------------
  exponent      = S("eE") * S("+-")**-1 * digit**1
  fraction      = "." * digit**1
  intpart       = digit**1
  pointfloat    = (intpart**-1 * fraction) + (intpart * ".")
  exponentfloat = (intpart + pointfloat) * exponent
  floatnumber   = pointfloat + exponentfloat  & 'hide'

  # ----------------------------------------------------------------------------
  # imaginary number
  # ----------------------------------------------------------------------------
  imagnumber = (floatnumber + intpart) * S("jJ") & 'hide'

  # ----------------------------------------------------------------------------
  # numbers
  # ----------------------------------------------------------------------------
  return "number" | integer + longinteger + floatnumber + imagnumber

# ==============================================================================
def STRING_():
  escapeseq       = "\\" * P(1)
  longstringchar  = P(1) - ("\\" + Cb("quote"))
  shortstringchar = P(1) - ("\\" + newline + Cb("quote"))
  longstringitem  = longstringchar + escapeseq
  shortstringitem = shortstringchar + escapeseq

  tripplequote    = P('"""') + P("'''")
  longstring      = 'longstring'  | Cb('quote', tripplequote) * \
                                    longstringitem**0 * Cb('quote')
  shortstring     = 'shortstring' | Cb("quote",quote) * \
                                    shortstringitem**0 * Cb("quote")

  stringprefix    =  S("rR") + S("uUbB") * S("rR")**-1
  stringliteral   =  stringprefix**-1 * (longstring + shortstring)

  return "string" | longstring + shortstring + stringliteral

# ==============================================================================

def pythonGrammar():
  # Function declaration
  Fd = lambda ptn: "Function Decl" | Cg(Cc('def')*C(ptn))
  Cd = lambda ptn: "Class Decl" | Cg(Cc('class')*C(ptn))
  END = Cg(Cc('end')*Cc(''))
  # Variable declaration
  Vd = lambda ptn: 'Variable Decl' | Cg(Cc('decl')*C(ptn))
  # Import all from a module
  Im = lambda ptn: 'Import all' | Cg(Cc('import all')*C(ptn))

  newline.setName('newline')

  # ----------------------------------------------------------------------------
  # Variables that appear in python code are either being declared (set) or used
  # We want to track the variables that appear and indicate whether they are
  # being declared or used. A 'var state' stack is created with the value 'var'
  # which indicates a variable is being used. If an assignment statement occurs,
  # a 'decl' value is added to the stack that indicates that the value is being
  # declared. This is popped from the stack when assignment ends.

  init_var_state = Sc('var state', Cc('var'))
  decl_state     = Sc('var state', Cc('decl'))    # Mark start of assignment (declare variables)
  cls_parent     = Sc('var state', Cc('parent'))  # Mark start of assignment (declare variables)
  #ignore_state   = Sc('var state', Cc('ignore'))  # Mark variables that are not really variable (named args to methods)
  pop_state      = Sp('var state')                # Mark end of assignment

  # Add a variable capture that is a declared variable or a used variable depending
  # on the 'var state' stack
  Va = lambda ptn: Cg(Cs('var state') * C(ptn))

  # ----------------------------------------------------------------------------
  # Smart Whitepace
  # ----------------------------------------------------------------------------

  comment = 'comment' | '#' * matchUntil(newline)

  ws0 = whitespace**0
  line_continuation = '\\' * ws0 * newline * ws0

  # This has optimization that checks for a continuation or a comment character
  # before looking further.
  ws = ws0 * (~P('\\')          * Ssz('Group', 0) * line_continuation**0 +
              ~(P('\\')+P('#') + newline) * (-Ssz('Group', 0))*
                                  (line_continuation +
                                   comment**-1 * newline * ws0)**0 +
              P(0)) & 'hide'

  # ----------------------------------------------------------------------------
  # Pattern Operators
  # ----------------------------------------------------------------------------

  # Stack capture and pop values from the 'Group' stack. This stack is used to
  # track parenthesis and other grouping operators
  SC = lambda ptn: Sc("Group", C(P.asPattern(ptn))) * ws
  SP = lambda ptn: P.asPattern(ptn) * Sp("Group") * ws

  # Distinguish between a variable starting with a keyword and a keyword
  var_char = alpha + digit + '_' & 'hide'
  KW = lambda ptn: (P.asPattern(ptn) * - var_char)*ws  # KEYWORD

  # Get pattern followed by whitespace
  Pw = lambda ptn: P.asPattern(ptn) * ws
  Sw = lambda ptn: S(ptn) * ws

  # ----------------------------------------------------------------------------
  # Atomic parts
  # ----------------------------------------------------------------------------

  STRING = STRING_() * ws
  NUMBER = NUMBER_() * ws
  NAME =  "name" | (alpha + '_' & 'hide') * (var_char)**0 * ws

  # ----------------------------------------------------------------------------

  def checkIndent(match):
    """
    Verify that the indent is greater than the previous indent
    """
    if match.context == None: return match
    indents = match.context.getStack("indent")
    if indents is None: return

    string = match.string
    if len(indents) < 2: return match

    # Check that the indentation is larger than previous indentation
    if len(indents[-1]) > len(indents[-2]):
      #TODO: Report an error
      pass

    # Check that the new contains the previous indentation characters
    if not indents[-1].startswith(indents[-2]):
      # TODO: report an error
      pass

    return match

  # ----------------------------------------------------------------------------

  def dedent(match):
    """
    Check for a valid dedent and remove indents from the indent stack
    """
    if match.context == None: return match
    indents = match.context.getStack("indent")

    # TODO: Report an invalid deindent
    if indents is None or len(indents) == 0: return

    indent = match.getValue()
    indentSz = len(indent)
    # TODO: report that the dedented line is actually indented
    if indentSz > len(indents.peek()): pass
    indents.pop() # Pop at least one indent from the stack

    return match

  # ----------------------------------------------------------------------------

  # TODO: Track the indentation and unindent
  INDENT = 'INDENT' | Sc('indent',C(ws)) / checkIndent
  DEDENT = 'DEDENT' | P(0) / dedent

  # The next_stmt_line should begin at the start of a line (or the end of the file)
  # It should NOT eat the whitespace since indentation is checked after this is
  # called.
  next_stmt_line = 'next_stmt_line' | (ws*comment**-1 * (newline + -P(1)))**1

  # This is called after next_stmt_line to check that the indentation is correct.
  # Failure of this pattern is used to detect a DEDENT
  match_indent = 'match_indent' | Sm('indent')*(-whitespace)

  # fpdef: NAME | '(' fplist ')'
  fpdef = 'fpdef' | Vd(NAME) + SC('(') * V('fplist') * SP(')')

  # fplist: fpdef (',' fpdef)* [',']
  fplist = 'fplist' | fpdef * (Pw(',') * fpdef)**0 * Pw(',')**-1

  # varargslist: ((fpdef ['=' test] ',')*
  #               ('*' NAME [',' '**' NAME] | '**' NAME) |
  #               fpdef ['=' test] (',' fpdef ['=' test])* [','])
  arg = 'arg' | fpdef * (Pw('=')*V('test'))**-1
  varargslist = 'varargslist' | (('varargslist1' | (arg * Pw(','))**0 *
                 (Pw('*')*Vd(NAME)*(Pw(',')*Pw('**')*Vd(NAME))**-1 + Pw('**')*Vd(NAME))) +
                ('varargslist2' | arg * (Pw(',')*arg)**0 * Pw(',')**-1)**0)

  # ----------------------------------------------------------------------------
  # Simple Statement
  # ----------------------------------------------------------------------------

  # augassign: ('+=' | '-=' | '*=' | '/=' | '%=' | '&=' | '|=' | '^=' |
  #             '<<=' | '>>=' | '**=' | '//=')
  augassign = 'augassign' | Pw('+=') + Pw('-=') + Pw('*=') + Pw('/=') + \
                            Pw('%=') + Pw('&=') + Pw('|=') + Pw('^=') + \
                            Pw('<<=') + Pw('>>=') + Pw('**=') + Pw('//=')

  assign = 'assign' | Pw('=')

  # # For normal assignments, additional restrictions enforced by the interpreter
  # expr_stmt: testlist (augassign (yield_expr|testlist) |
  #                      ('=' (yield_expr|testlist))*)
  capture_assign = decl_state * V('testlist') * pop_state
  expr_stmt = 'expr_stmt' | (capture_assign * augassign* (V('yield_expr')+V('testlist')) +
                             capture_assign * (assign*(V('yield_expr')+V('testlist')))**1 +
                             V('testlist'))

  # print_stmt: 'print' ( [ test (',' test)* [','] ] |
  #                       '>>' test [ (',' test)+ [','] ] )
  print_stmt = 'print_stmt' | KW('print') * ((V('test') *
                (Pw(',')*V('test'))**0 * (Pw(','))**-1)**-1 +
                Pw('>>')*V('test')*((Pw(',')*V('test')*(Pw(','))**-1)**0)**-1)

  # del_stmt: 'del' exprlist
  del_stmt = 'del_stmt' | KW('del') * V('exprlist')

  # pass_stmt: 'pass'
  pass_stmt = 'pass_stmt' | KW('pass')

  # break_stmt: 'break'
  break_stmt = 'break_stmt' | KW('break')

  # continue_stmt: 'continue'
  continue_stmt = 'continue_stmt' | KW('continue')

  # return_stmt: 'return' [testlist]
  return_stmt = 'return_stmt' | KW('return') * (~newline + V('testlist'))

  # raise_stmt: 'raise' [test [',' test [',' test]]]
  raise_stmt = 'raise_stmt' | KW('raise') * (V('test') * (Pw(',')*V('test') *
                                            (Pw(',')*V('test'))**-1)**-1)**-1

  # yield_stmt: yield_expr
  yield_stmt = V('yield_expr')

  # flow_stmt: break_stmt | continue_stmt | return_stmt | raise_stmt | yield_stmt
  flow_stmt = 'flow_stmt' | break_stmt + continue_stmt + return_stmt + raise_stmt + yield_stmt

  # dotted_name: NAME ('.' NAME)*
  dotted_name = 'dotted_name' | NAME * (Pw(".") * NAME)**0

  # dotted_as_name: dotted_name ['as' NAME]
  dotted_as_name = 'dotted_as_name' | dotted_name * KW('as') * Vd(NAME) + Vd(dotted_name)

  # dotted_as_names: dotted_as_name (',' dotted_as_name)*
  dotted_as_names = 'dotted_as_names' | dotted_as_name * (Pw(',') * dotted_as_name)**0

  # import_name: 'import' dotted_as_names
  import_name = 'import_name' | KW('import') * dotted_as_names

  # import_as_name: NAME ['as' NAME]
  import_as_name = 'import_as_name' | NAME * KW('as') * Vd(NAME) + Vd(NAME)

  # import_as_names: import_as_name (',' import_as_name)* [',']
  import_as_names = 'import_as_names' | import_as_name * (Pw(',')*import_as_name)**0 * Pw(',')**-1

  # import_from: ('from' ('.'* dotted_name | '.'+) 'import' ('*' | '(' import_as_names ')' | import_as_names))
  import_from = 'import_from' | \
      KW('from') * Im(Pw('.') ** 0 * dotted_name + Pw('.') ** 1) * KW('import') * Pw('*') \
      + \
      KW('from') * (Pw('.')**0*dotted_name + Pw('.')**1) * KW('import') * (SC('(')*import_as_names*SP(')') + import_as_names)

  # import_stmt: import_name | import_from
  import_stmt = 'import_stmt' | import_name + import_from

  # global_stmt: 'global' NAME (',' NAME)*
  global_stmt = 'global_stmt' | KW('global')*NAME*(Pw(',')*NAME)**0

  # exec_stmt: 'exec' expr ['in' test [',' test]]
  exec_stmt = 'exec_stmt' | KW('exec')*V('expr')*(KW('in')*V('test') * (Pw(',')*V('test'))**-1)**-1

  # assert_stmt: 'assert' test [',' test]
  assert_stmt = 'assert_stmt' | KW('assert') * V('test') * (Pw(',')*V('test'))**-1

  # small_stmt: (expr_stmt | print_stmt  | del_stmt | pass_stmt | flow_stmt |
  #              import_stmt | global_stmt | exec_stmt | assert_stmt)
  small_stmt = 'small_stmt' | print_stmt + del_stmt + pass_stmt + \
               flow_stmt + import_stmt + global_stmt + exec_stmt + assert_stmt + expr_stmt

  # simple_stmt: small_stmt (';' small_stmt)* [';'] NEWLINE
  simple_stmt = 'simple_stmt' | small_stmt * (Pw(';')*small_stmt)**0 * Pw(';')**-1 * next_stmt_line

  # ----------------------------------------------------------------------------
  # Compound Statement
  # ----------------------------------------------------------------------------

  # suite: simple_stmt | NEWLINE INDENT stmt+ DEDENT
  suite = 'suite' | next_stmt_line * INDENT * V('stmt') * (match_indent * V('stmt'))**0 * DEDENT + simple_stmt

  # if_stmt: 'if' test ':' suite ('elif' test ':' suite)* ['else' ':' suite]
  if_stmt = 'if_stmt' | KW('if')*V('test')*Pw(':')*suite* \
         (match_indent*KW('elif')*V('test')*Pw(':')*suite)**0 * \
         (match_indent*KW('else')*Pw(':')*suite)**-1

  # while_stmt: 'while' test ':' suite ['else' ':' suite]
  suite_else =  suite * (match_indent*KW('else')*Pw(':')*suite)**-1
  while_stmt = 'while_stmt' | KW('while') * V('test')*Pw(':') * suite_else

  # for_stmt: 'for' exprlist 'in' testlist ':' suite ['else' ':' suite]
  for_stmt = 'for_stmt' | KW('for') * decl_state * V('exprlist') * pop_state * \
                          KW('in') * V('testlist') * Pw(':') * suite_else

  # # NB compile.c makes sure that the default except clause is last
  # except_clause: 'except' [test [('as' | ',') test]]
  except_clause = 'except_clause' | KW('except') * \
            (V('test') * ((KW('as') + Pw(',')) * decl_state*V('test')*pop_state)**-1)**-1

  # try_stmt: ('try' ':' suite
  #            ((except_clause ':' suite)+
  #             ['else' ':' suite]
  #             ['finally' ':' suite] |
  #            'finally' ':' suite))
  try_stmt = 'try_stmt' | KW('try')      * Pw(':') * suite * \
                          (match_indent * except_clause  * Pw(':') * suite *
                          (match_indent * KW('else')    * Pw(':') * suite)**-1 *
                          (match_indent * KW('finally') * Pw(':') * suite)**-1
                          +
                          (match_indent * KW('finally') * Pw(':') * suite)**-1)

  # with_item: test ['as' expr]
  with_item = 'with_item' | V('test') * (KW('as') * decl_state*V('expr')*pop_state)**-1

  # with_stmt: 'with' with_item (',' with_item)*  ':' suite
  with_stmt = 'with_stmt' | KW('with') * with_item *(Pw(',')*with_item)**0 * Pw(':') * suite

  # # The reason that keywords are test nodes instead of NAME is that using NAME
  # # results in an ambiguity. ast.c makes sure it's a NAME.
  # argument: test [comp_for] | test '=' test
  argument = 'argument' | V('test') * Pw('=') * V('test') + \
                          V('test') * V('comp_for')  + \
                          V('test')

  # arglist: (argument ',')* (argument [',']
  #                          |'*' test (',' argument)* [',' '**' test]
  #                          |'**' test)
  arglist = 'arglist' | (argument*Pw(','))**0 * (argument * Pw(',')**-1 +
                         Pw('*')*V('test')*(Pw(',')*argument)**0*(Pw(',')*Pw('**')*V('test'))**-1 +
                         Pw('**') * V('test'))

  # decorator: '@' dotted_name [ '(' [arglist] ')' ] NEWLINE
  # decorators: decorator+
  decorator  = 'decorator' | Pw('@') * dotted_name * \
                             (SC('(') * arglist**-1 * SP(')'))**0 * next_stmt_line
  decorators = 'decorators' | decorator*(match_indent*decorator**0)

  # parameters: '(' [varargslist] ')'
  parameters = 'parameters' | SC('(') * varargslist**-1 * SP(')')

  # funcdef: 'def' NAME parameters ':' suite
  funcdef = 'funcdef' | KW('def') * Fd(NAME) * parameters * Pw(':') * suite * END

  # classdef: 'class' NAME ['(' [testlist] ')'] ':' suite
  classdef = 'classdef' | KW('class') * Cd(NAME) * \
                          (SC('(') * cls_parent*V('testlist')*pop_state * SP(')'))**-1 * Pw(':') * \
                          suite * END

  # decorated: decorators (classdef | funcdef)
  decorated = 'decorated' | decorators * (classdef + funcdef)

  # compound_stmt: if_stmt | while_stmt | for_stmt | try_stmt | with_stmt | funcdef | classdef | decorated
  compound_stmt = 'compount_stmt' | if_stmt + while_stmt + for_stmt + try_stmt + with_stmt + funcdef + classdef + decorated

  # ----------------------------------------------------------------------------
  # Statement
  # ----------------------------------------------------------------------------

  # stmt: simple_stmt | compound_stmt
  stmt = 'stmt' | ~P(1)*(compound_stmt + simple_stmt)

  # ----------------------------------------------------------------------------
  # Test
  # ----------------------------------------------------------------------------

  # comp_op: '<' | '>' | '==' | '>=' | '<=' | '<>' | '!=' | 'in' | 'not' 'in' | 'is' | 'is' 'not'
  comp_op = 'comp_op' | Pw('==') + Pw('>=') + Pw('<=') + Pw('<>') + Pw('!=') + \
                        Pw('<') + Pw('>') + KW('not')*KW('in') + KW('in') + \
                        KW('is')*KW('not') + KW('is')

  # comparison: expr (comp_op expr)*
  comparison = 'comparison' | V('expr') * (comp_op*V('expr'))**0

  # not_test: 'not' not_test | comparison
  not_test = 'not_test' | KW('not')**0  * comparison

  # and_test: not_test ('and' not_test)*
  and_test = 'and_test' | not_test * (KW('and') * not_test)**0

  # or_test: and_test ('or' and_test)*
  or_test = 'or_test' | and_test * (KW('or') * and_test)**0

  # lambdef: 'lambda' [varargslist] ':' test
  lambdef = 'lambdef' | KW('lambda') * (varargslist)**-1 * Pw(':') * V('test')

  # test: or_test ['if' or_test 'else' test] | lambdef
  test = 'test' | lambdef + or_test * (KW('if')*or_test*KW('else')*V('test'))**-1

  # testlist: test (',' test)* [',']
  testlist = 'testlist' | test * (Pw(',') * test)**0 * Pw(',')**-1

  # testlist1: test (',' test)*
  testlist1 = 'testlist1' | test * (Pw(',') * test)**0

  # ----------------------------------------------------------------------------
  # Factor
  # ----------------------------------------------------------------------------

  # sliceop: ':' [test]
  sliceop = 'sliceop' | Pw(':') * (test)**-1

  # subscript: '.' '.' '.' | test | [test] ':' [test] [sliceop]
  subscript = 'subscript' | Pw('.')*Pw('.')*Pw('.') + (test)**-1 *Pw(':') * (test)**-1 * (sliceop)**-1 + test

  # subscriptlist: subscript (',' subscript)* [',']
  subscriptlist = 'subscriptlist' | subscript * (Pw(',')*subscript)**0 * Pw(',')**-1

  # trailer: '(' [arglist] ')' | '[' subscriptlist ']' | '.' NAME
  trailer = 'trailer' | SC('(') * (arglist)**-1 * SP(')') + \
                        SC('[') * subscriptlist * SP(']') + \
                        Pw('.') * NAME

  # factor: ('+' | '-' | '~') factor | power
  factor = 'factor' | Sw('+-~')**0 * V('power')

  # ----------------------------------------------------------------------------
  # Atom
  # ----------------------------------------------------------------------------

  # # Backward compatibility cruft to support:
  # # [ x for x in lambda: True, lambda: False if x() ]
  # # even while also allowing:
  # # lambda x: 5 if x else 2
  # # (But not a mix of the two)
  # old_lambdef: 'lambda' [varargslist] ':' old_test
  old_lambdef = KW('lambda') * (varargslist) ** -1 * Pw(':') * V('old_test')

  # old_test: or_test | old_lambdef
  old_test = 'old_test' | or_test + old_lambdef

  # testlist_safe: old_test [(',' old_test)+ [',']]
  testlist_safe = old_test * ((Pw(',') * old_test) ** 1 *  Pw(',')**-1)**-1

  # comp_for: 'for' exprlist 'in' or_test [comp_iter]
  comp_for = 'comp_for' | KW('for')* V('exprlist') * KW('in') * or_test * V('comp_iter')**-1

  # comp_if: 'if' old_test [comp_iter]
  comp_if = KW('if') * old_test * V('comp_iter')**-1

  # comp_iter: comp_for | comp_if
  comp_iter = 'comp_iter' | comp_for + comp_if

  # dictorsetmaker: ( (test ':' test (comp_for | (',' test ':' test)* [','])) |
  #                   (test (comp_for | (',' test)* [','])) )
  dictorsetmaker = 'dictorsetmaker' | (test*Pw(':')*test*(comp_for + (Pw(',')*test*Pw(':')*test)**0 * Pw(',')**-1)) + \
                   (test * (comp_for + (Pw(',') * test)**0 * Pw(',')**-1))


  # list_iter: list_for | list_if
  list_iter = V('list_for') + V('list_if')

  # list_for: 'for' exprlist 'in' testlist_safe [list_iter]
  list_for = 'list_for' | KW('for') * V('exprlist') * KW('in') * testlist_safe * list_iter**-1

  # list_if: 'if' old_test [list_iter]
  list_if = 'list_if' | KW('if') * old_test * list_iter**-1

  # listmaker: test ( list_for | (',' test)* [','] )
  listmaker = 'listmaker' | test * (list_for + (Pw(',') * test)**0 * Pw(',')**-1)

  # testlist_comp: test ( comp_for | (',' test)* [','] )
  testlist_comp = 'testlist_comp' | test * (comp_for + (Pw(',') * test)**0 * Pw(',')**-1)

  # yield_expr: 'yield' [testlist]
  yield_expr = 'yield_expr' | KW('yield') * (testlist)**-1

  # atom: ('(' [yield_expr|testlist_comp] ')' |
  #        '[' [listmaker] ']' |
  #        '{' [dictorsetmaker] '}' |
  #        '`' testlist1 '`' |
  #        NAME | NUMBER | STRING+)
  atom = 'atom' | SC('(') * (yield_expr +  testlist_comp)**-1 * SP(')') + \
                  SC('[') * listmaker**-1 * SP(']') + \
                  SC('{') * dictorsetmaker**-1 * SP('}') + \
                  SC('`') * testlist1 * SP('`') + \
                  STRING**1 + Va(NAME) + NUMBER

  # ----------------------------------------------------------------------------
  # Expression
  # ----------------------------------------------------------------------------

  # power: atom trailer* ['**' factor]
  dotted_atom = NAME * (Pw('.') * NAME)**1
  power = 'power' | (Va(dotted_atom) + atom) * trailer**0 * (Pw('**') * factor)**-1

  # term: factor (('*' | '/' | '%' | '//') factor)*
  term = 'term' | factor *((Pw('//') + Sw('*/%')) * factor)**0

  # arith_expr: term (('+' | '-') term)*
  arith_expr = 'arith_expr' | term * (Sw('+-') * term)**0

  # shift_expr: arith_expr (('<<' | '>>') arith_expr)*
  shift_expr = 'shift_expr' | arith_expr * ((Pw('<<') + Pw('>>')) * arith_expr)**0

  # and_expr: shift_expr ('&' shift_expr)*
  and_expr = 'and_expr' | shift_expr * (Pw('&') * shift_expr)**0

  # xor_expr: and_expr ('^' and_expr)*
  xor_expr = 'xor_expr' | and_expr * (Pw('^') * and_expr)**0

  # expr: xor_expr ('|' xor_expr)*
  expr = 'expr' | xor_expr * (Pw('|') * xor_expr)**0

  # exprlist: expr (',' expr)* [',']
  exprlist = 'exprlist' | expr * (Pw(',') * expr)**0 * Pw(',')**-1

  # ----------------------------------------------------------------------------
  # File input
  # ----------------------------------------------------------------------------

  # Allow the first statement to be indented. Include the first statement indent
  # in the indents stack.

  # file_input: (NEWLINE | stmt)* ENDMARKER
  file_input = 'file_input' | init_var_state * next_stmt_line**-1 * \
                              (INDENT * stmt)**-1 * (match_indent*stmt)**0

  # ----------------------------------------------------------------------------
  # Close grammar
  # ----------------------------------------------------------------------------

  setVs(fpdef,         [fplist])
  setVs(varargslist,   [test])
  setVs(expr_stmt,     [testlist, yield_expr])
  setVs(print_stmt,    [test])
  setVs(del_stmt,      [exprlist])
  setVs(return_stmt,   [testlist])
  setVs(raise_stmt,    [test])
  setVs(yield_stmt,    [yield_expr])
  setVs(exec_stmt,     [test])
  setVs(assert_stmt,   [test])
  setVs(suite,         [stmt])
  setVs(if_stmt,       [test])
  setVs(while_stmt,    [test])
  setVs(for_stmt,      [exprlist, testlist])
  setVs(except_clause, [test])
  setVs(with_item,     [test, expr])
  setVs(argument,      [test, comp_for])
  setVs(arglist,       [test])
  setVs(classdef,      [testlist])
  setVs(testlist,      [test])
  setVs(comparison,    [expr])
  setVs(old_lambdef,   [old_test])
  setVs(comp_for,      [exprlist, comp_iter])
  setVs(comp_if,       [comp_iter])
  setVs(lambdef,       [test])
  setVs(test,          [test])
  setVs(list_iter,     [list_for, list_if])
  setVs(list_for,      [exprlist])
  setVs(factor,        [power])

  #varargslist.debug(True)
  return file_input

# ==============================================================================

def getUndefinedVarsFromSrc(src):
  """
  Parse the source code and get a list of the variables that are undefined in
  the source code.

  :param src: A string with the source code to parse.
  :return: An array of undefined variables.
  """
  defined, scope, undefined = ([], [], [])

  # First add the builtins to the list of defined variables
  defined.extend(dir(__builtins__))
  scope.append(len(defined)) # Mark the end of this scope

  pygrammar = pythonGrammar()
  match = pygrammar.match(src)

  # This needs to be more sophisticated to handle class variables where
  # self.<classvar> is used, and things like static methods are possible.
  for cmd, val in match.captures:
    val = val.strip()

    if cmd == 'end':
      end_of_scope = scope.pop()
      defined = defined[:end_of_scope]
      continue

    if cmd in ("class","def"):
      # Add the class to the current scope and mark start of new scope
      defined.append(val)
      scope.append(len(defined))
      continue

    if cmd == "parent":
      defined.append(val)
      scope[-1] = len(defined) # Move the scope forward to include the parent object
      continue

    if cmd == "decl":
      defined.append(val)
      continue

    if cmd == "var" and val not in defined:
      undefined.append(val)

  return undefined

# ==============================================================================

def printValuesUsedInSrc(src):
  pygrammar = pythonGrammar()
  #pygrammar.debug(True)

  match = pygrammar.match(src)

  def show(string):
    print "  " * indent + string.strip()

  indent = 0
  for cmd, val in match.captures:
    if cmd == 'end':
      indent -= 1
      continue

    show("{0} {1} ".format(cmd, val))
    if cmd in ("class", "def"):
      indent += 1

# ==============================================================================

if __name__ == "__main__":
  with open("PyPE/Tokenizer.py") as file:
    code = file.read()

  #print getUndefinedVarsFromSrc(code)

  pyg = pythonGrammar()

  print pyg.match(code)