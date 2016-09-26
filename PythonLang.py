from PyPE import P, S, R, C, Cc, Cb, Cg, SOL, EOL, alpha, digit, newline, \
                 quote, V, setVs, Sc, Sp, Sm, matchUntil, whitespace

# kw = P('and') + P('as') + P('assert') + P('break') + P('class') + P('continue') + \
#      P('def') + P('del') + P('elif') + P('else') + P('except') + P('exec') + \
#      P('finally') + P('for') + P('from') + P('global') + P('if') + P('import') + \
#      P('in') + P('is') + P('lambda') + P('not') + P('or') + P('pass') + \
#      P('print') + P('raise') + P('return') + P('try') + P('while') + P('with') + \
#      P('yield')

# ==============================================================================
def NUMBER():
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
def STRING():
  escapeseq       = "\\" * P(1)
  longstringchar  = P(1) - "\\"
  shortstringchar = P(1) - ("\\" + newline + quote)
  longstringitem  = longstringchar + escapeseq
  shortstringitem = shortstringchar + escapeseq

  longstring      = ("'''" * longstringitem**0 * "'''" +
                     '"""' * longstringitem**0 * '"""')  & "hide"
  shortstring     = Cb("quote",quote) * shortstringitem**0 * Cb("quote")  & "hide"

  stringprefix    =  S("rR") + S("uUbB") * S("rR")**-1
  stringliteral   =  stringprefix**-1 * (shortstring + longstring)  & "hide"

  return "string" | longstring + shortstring + stringliteral

# ==============================================================================
def PythonGrammar():
  ws = (P(whitespace) & 'hide')**0
  ws1 = (P(whitespace) & 'hide')**1
  newline.setName('newline')

  # ----------------------------------------------------------------------------

  def checkIndent(match):
    """
    Verify that the indent is greater than the previous indent
    """
    if match.context == None: return match
    indents = match.context.getStack("indent")
    if indents is None: return

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
  INDENT = 'INDENT' | (ws * newline)**0 * Sc('indent',C(ws)) / checkIndent
  DEDENT = 'DEDENT' | P(0) / dedent

  comment = 'comment' | '#' * matchUntil(newline)
  next_stmt_line = 'next_stmt_line' | (ws * comment**-1 * (newline + -P(1)))**1
  match_indent = 'match_indent' | (Sm('indent')*(-whitespace) + P(0))

  NAME =  "name" | (alpha + '_' & 'hide') * (alpha + digit + '_' & 'hide')**0

  # fpdef: NAME | '(' fplist ')'
  fpdef = 'fpdef' | NAME + '(' *ws* V('fplist') *ws* ')'

  # fplist: fpdef (',' fpdef)* [',']
  fplist = 'fplist' | fpdef * (ws*',' *ws* fpdef)**0 *ws* P(',')**-1

  # varargslist: ((fpdef ['=' test] ',')*
  #               ('*' NAME [',' '**' NAME] | '**' NAME) |
  #               fpdef ['=' test] (',' fpdef ['=' test])* [','])
  varargslist = 'varargslist' | ((fpdef *ws* ('='*ws*V('test'))**-1 *ws* ',' )**0 *
                 ('*' *ws* NAME *ws* (','*ws*'**'*ws*NAME)**-1 + '**'*ws*NAME) +
                 fpdef *ws* ('='*ws*V('test'))**-1 *ws* (','*ws*fpdef*ws*('='*ws*V('test'))**-1 *ws* P(',')**-1)**0)

  # augassign: ('+=' | '-=' | '*=' | '/=' | '%=' | '&=' | '|=' | '^=' |
  #             '<<=' | '>>=' | '**=' | '//=')
  augassign = 'augassign' | P('+=') + P('-=') + P('*=') + P('/=') + P('%=') + P('&=') + P('|=') + \
              P('^=') + P('<<=') + P('>>=') + P('**=') + P('//=')

  assign = 'assign' | P('=')

  # ----------------------------------------------------------------------------
  # Simple Statement
  # ----------------------------------------------------------------------------

  # expr_stmt: testlist (augassign (yield_expr|testlist) |
  #                      ('=' (yield_expr|testlist))*)
  expr_stmt = 'expr_stmt' | V('testlist') * (ws*augassign*ws* (V('yield_expr')+V('testlist')) +
                               (ws*assign*ws*(V('yield_expr')+V('testlist')))**0)

  # # For normal assignments, additional restrictions enforced by the interpreter
  # print_stmt: 'print' ( [ test (',' test)* [','] ] |
  #                       '>>' test [ (',' test)+ [','] ] )
  print_stmt = 'print_stmt' | 'print' * (ws*(V('test') * (ws*','*ws*V('test'))**0 * (ws*P(','))**-1)**-1 +
                          '>>'*ws*V('test')*((ws*','*ws*V('test')*(P(','))**-1 )**0)**-1)

  # del_stmt: 'del' exprlist
  del_stmt = 'del_stmt' | 'del' *ws* V('exprlist')

  # pass_stmt: 'pass'
  pass_stmt = 'pass_stmt' | P('pass')

  # break_stmt: 'break'
  break_stmt = P('break')

  # continue_stmt: 'continue'
  continue_stmt = P('continue')

  # return_stmt: 'return' [testlist]
  return_stmt = 'return' * V('testlist')

  # raise_stmt: 'raise' [test [',' test [',' test]]]
  raise_stmt = 'raise_stmt' | 'raise' * (ws1*V('test') * (ws*','*ws*V('test') *
                                        (ws*','*ws*V('test'))**-1)**-1)**-1

  # yield_stmt: yield_expr
  yield_stmt = V('yield_expr')

  # flow_stmt: break_stmt | continue_stmt | return_stmt | raise_stmt | yield_stmt
  flow_stmt = 'flow_stmt' | break_stmt + continue_stmt + return_stmt + raise_stmt + yield_stmt

  # dotted_name: NAME ('.' NAME)*
  dotted_name = 'dotted_name' | NAME * ("." * NAME)**0

  # dotted_as_name: dotted_name ['as' NAME]
  dotted_as_name = dotted_name * (ws1*'as'*ws1*NAME)**-1

  # dotted_as_names: dotted_as_name (',' dotted_as_name)*
  dotted_as_names = dotted_as_name * (ws* ',' *ws* dotted_as_name)**0

  # import_name: 'import' dotted_as_names
  import_name = 'import_name' | 'import' *ws1* dotted_as_names

  # import_as_name: NAME ['as' NAME]
  import_as_name = 'import_as_name' | NAME * (ws1*'as'*ws1*NAME)**-1

  # import_as_names: import_as_name (',' import_as_name)* [',']
  import_as_names = 'import_as_names' | import_as_name * (ws*','*import_as_name)**0 * (ws*P(','))**-1

  # import_from: ('from' ('.'* dotted_name | '.'+)
  #               'import' ('*' | '(' import_as_names ')' | import_as_names))
  import_from = 'import_from' | 'from' *ws1* (P('.')**0*dotted_name + P('.')**1) *ws* \
                'import' * (ws*'*' + '('*ws*import_as_name*ws*')' )

  # import_stmt: import_name | import_from
  import_stmt = 'import_stmt' | import_name + import_from

  # global_stmt: 'global' NAME (',' NAME)*
  global_stmt = 'global_stmt' | 'global'*ws1*NAME*(ws*','*ws*NAME)**0

  # exec_stmt: 'exec' expr ['in' test [',' test]]
  exec_stmt = 'exec_stmt' | 'exec'*ws1*V('expr')*(ws1*'in'*V('test') * (ws*','*ws*V('test'))**-1)**-1

  # assert_stmt: 'assert' test [',' test]
  assert_stmt = 'assert_stmt' | 'assert' *ws1* V('test') * (ws*','*V('test'))**-1

  # small_stmt: (expr_stmt | print_stmt  | del_stmt | pass_stmt | flow_stmt |
  #              import_stmt | global_stmt | exec_stmt | assert_stmt)
  small_stmt = 'small_stmt' | print_stmt + del_stmt + pass_stmt + \
               flow_stmt + import_stmt + global_stmt + exec_stmt + assert_stmt + expr_stmt

  # simple_stmt: small_stmt (';' small_stmt)* [';'] NEWLINE
  simple_stmt = 'simple_stmt' | small_stmt * (ws*';'*ws*small_stmt)**0 * (ws*P(';'))**-1 * next_stmt_line

  # ----------------------------------------------------------------------------
  # Compound Statement
  # ----------------------------------------------------------------------------

  # suite: simple_stmt | NEWLINE INDENT stmt+ DEDENT
  suite = 'suite' | next_stmt_line * INDENT * V('stmt') * (match_indent * V('stmt'))**0 * DEDENT + simple_stmt

  # if_stmt: 'if' test ':' suite ('elif' test ':' suite)* ['else' ':' suite]
  if_stmt = 'if_stmt' | 'if'*ws*V('test')*ws*':'*suite

  # while_stmt: 'while' test ':' suite ['else' ':' suite]
  suite_else =  suite * ('else'*ws*':'*suite)**-1
  while_stmt = 'while_stmt' | 'while' *ws1* V('test')*ws*':' * suite_else

  # for_stmt: 'for' exprlist 'in' testlist ':' suite ['else' ':' suite]
  for_stmt = 'for_stmt' | 'for' *ws1* V('exprlist') *ws1* 'in' *ws1* V('testlist')*ws*':' * suite_else

  # # NB compile.c makes sure that the default except clause is last
  # except_clause: 'except' [test [('as' | ',') test]]
  except_clause = 'except_clause' | 'except' * (ws1* V('test') * ((ws1*'as'*ws1 + ws*','*ws)*V('test'))**-1)**-1

  # try_stmt: ('try' ':' suite
  #            ((except_clause ':' suite)+
  #             ['else' ':' suite]
  #             ['finally' ':' suite] |
  #            'finally' ':' suite))
  try_stmt = 'try_stmt' | 'try'*ws*':' * suite * (
                          except_clause *ws*':' * suite *
                          ('else'*ws*':' * suite)**-1 *
                          ('finally'*ws*':' * suite)**-1
                          +
                          ('finally'*ws*':' * suite)**-1)

  # with_item: test ['as' expr]
  with_item = 'with_item' | V('test') * (ws1*'as'*ws1*V('expr'))**-1

  # with_stmt: 'with' with_item (',' with_item)*  ':' suite
  with_stmt = 'with_stmt' | 'with' *ws1* with_item *(ws*','*ws*with_item)**0 *ws*':' * suite

  # # The reason that keywords are test nodes instead of NAME is that using NAME
  # # results in an ambiguity. ast.c makes sure it's a NAME.
  # argument: test [comp_for] | test '=' test
  argument = 'argument' | V('test') *ws* (V('comp_for'))**-1 + V('test') *ws*'='*ws* V('test')

  # arglist: (argument ',')* (argument [',']
  #                          |'*' test (',' argument)* [',' '**' test]
  #                          |'**' test)
  arglist = 'arglist' | (argument*ws*',')**0 * (argument * (ws*',')**-1 +
                                    ws*'*'*ws*V('test')*(ws*','*ws*argument)**0*(ws*',' * '**' * V('test'))**-1 +
                                    ws * '**' * V('test'))

  # decorator: '@' dotted_name [ '(' [arglist] ')' ] NEWLINE
  # decorators: decorator+
  decorator  = 'decorator' | '@' *ws* dotted_name *ws* \
                             ('(' *ws* arglist**-1 *ws* ')')**0 *ws* newline
  decorators = 'decorators' | decorator**1

  # parameters: '(' [varargslist] ')'
  parameters = 'parameters' | '(' *ws* varargslist**-1 *ws* ')'

  # funcdef: 'def' NAME parameters ':' suite
  funcdef = 'funcdef' | 'def' *ws1* NAME *ws* parameters *ws* ':' * V('suite')

  # testlist: test (',' test)* [',']
  testlist = 'testlist' | V('test') * (ws*','*ws*V('test'))**0 * (ws*',')**-1

  # classdef: 'class' NAME ['(' [testlist] ')'] ':' suite
  classdef = 'classdef' | 'class' *ws1* NAME * ('('*ws*testlist*ws*')')**-1 * ':' *suite

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

  # comp_op: '<'|'>'|'=='|'>='|'<='|'<>'|'!='|'in'|'not' 'in'|'is'|'is' 'not'
  comp_op = 'comp_op' | P('<') + P('>') + P('==') + P('>=') + P('<=') + P('<>') + P('!=') + \
            P('in') + P('not')*ws1*P('in') + P('is') + P('is')*ws1*P('not')

  # comparison: expr (comp_op expr)*
  comparison = 'comparison' | V('expr') * (ws*comp_op*ws*V('expr'))**0

  # not_test: 'not' not_test | comparison
  not_test = 'not_test' | ('not'*ws1)**0  * comparison

  # and_test: not_test ('and' not_test)*
  and_test = 'and_test' | not_test * (ws1*'and'*ws1* not_test)**0

  # or_test: and_test ('or' and_test)*
  or_test = 'or_test' | and_test * (ws1*'or'*ws1 * and_test)**0

  # lambdef: 'lambda' [varargslist] ':' test
  lambdef = 'lambda' *ws1* (varargslist)**-1 *ws*':' * V('test')

  # test: or_test ['if' or_test 'else' test] | lambdef
  test = 'test' | or_test * (ws1*'if'*ws*or_test*ws1*'else'*ws1*V('test'))**-1 + lambdef

  # ----------------------------------------------------------------------------
  # Factor
  # ----------------------------------------------------------------------------

  # sliceop: ':' [test]
  sliceop = 'sliceop' | ':' *ws* (test)**-1

  # subscript: '.' '.' '.' | test | [test] ':' [test] [sliceop]
  subscript = 'subscript' | '.' *ws* '.' *ws* '.' + test + (test)**-1 *ws*':'*ws * (test)**-1 * (sliceop)**-1

  # subscriptlist: subscript (',' subscript)* [',']
  subscriptlist = 'subscriptlist' | subscript * (ws*','*ws*subscript)**0 *ws* P(',')**-1

  # trailer: '(' [arglist] ')' | '[' subscriptlist ']' | '.' NAME
  trailer = 'trailer' | ws*'(' *ws* (arglist)**-1 *ws* ')' + ws*'[' *ws* subscriptlist *ws* ']' + '.' * NAME

  # factor: ('+'|'-'|'~') factor | power
  factor = 'factor' | (S('+-~')*ws)**0 * V('power')

  # ----------------------------------------------------------------------------
  # Atom
  # ----------------------------------------------------------------------------

  # # Backward compatibility cruft to support:
  # # [ x for x in lambda: True, lambda: False if x() ]
  # # even while also allowing:
  # # lambda x: 5 if x else 2
  # # (But not a mix of the two)
  # old_lambdef: 'lambda' [varargslist] ':' old_test
  old_lambdef = 'lambda' * ws1 * (varargslist) ** -1 * ws * ':' * V('old_test')

  # old_test: or_test | old_lambdef
  old_test = 'old_test' | or_test + old_lambdef

  # testlist_safe: old_test [(',' old_test)+ [',']]
  testlist_safe = old_test * ws * ((',' * ws * old_test) ** 1 * ws * P(
    ',') ** -1) ** -1

  # comp_for: 'for' exprlist 'in' or_test [comp_iter]
  comp_for = 'comp_for' | 'for' *ws1* V('exprlist') *ws1* 'in' *ws1* or_test * V('comp_iter')**-1

  # comp_if: 'if' old_test [comp_iter]
  comp_if = 'if' * ws1 * old_test * V('comp_iter')**-1

  # comp_iter: comp_for | comp_if
  comp_iter = 'comp_iter' | comp_for + comp_if

  # dictorsetmaker: ( (test ':' test (comp_for | (',' test ':' test)* [','])) |
  #                   (test (comp_for | (',' test)* [','])) )
  dictorsetmaker = 'dictorsetmaker' | (test *ws*':'*ws* test *ws* (comp_for + (',' *ws* test *ws*':'*ws)**0 * P(',')**-1)) + \
                   (test *ws* (comp_for + (',' *ws* test*ws)**0 * P(',')**-1))


  # list_iter: list_for | list_if
  list_iter = V('list_for') + V('list_if')

  # list_for: 'for' exprlist 'in' testlist_safe [list_iter]
  list_for = 'list_for' | 'for' *ws1* V('exprlist') *ws1* 'in' *ws1* testlist_safe * list_iter**-1

  # list_if: 'if' old_test [list_iter]
  list_if = 'list_if' | 'if' *ws* old_test *ws* list_iter**-1

  # listmaker: test ( list_for | (',' test)* [','] )
  listmaker = 'listmaker' | test *ws* (list_for + (',' *ws* test*ws)**0 * P(',')**-1)

  # testlist_comp: test ( comp_for | (',' test)* [','] )
  testlist_comp = 'testlist_comp' | test *ws* (comp_for + (',' *ws* test *ws)**0 * P(',')**-1)

  # yield_expr: 'yield' [testlist]
  yield_expr = 'yield_expr' | 'yield' *ws1* (testlist)**-1

  # testlist1: test (',' test)*
  testlist1 = 'testlist1' | test *ws* (',' *ws* test*ws)**0

  # atom: ('(' [yield_expr|testlist_comp] ')' |
  #        '[' [listmaker] ']' |
  #        '{' [dictorsetmaker] '}' |
  #        '`' testlist1 '`' |
  #        NAME | NUMBER | STRING+)
  atom = 'atom' | ( '(' *ws* (yield_expr +  testlist_comp)**-1 *ws* ')' +
           '[' *ws* listmaker**-1 *ws* ']' +
           '{' *ws* dictorsetmaker**-1 *ws* '}' +
           '`' * testlist1 * '`' +
           NAME + NUMBER() + (STRING()*ws)**1)

  # ----------------------------------------------------------------------------
  # Expression
  # ----------------------------------------------------------------------------

  # power: atom trailer* ['**' factor]
  power = 'power' | atom * trailer**0 * (ws*'**'*ws * factor)**-1

  # term: factor (('*'|'/'|'%'|'//') factor)*
  term = 'term' | factor *(ws* (P('//') + S('*/%')) *ws* factor)**0

  # arith_expr: term (('+'|'-') term)*
  arith_expr = 'arith_expr' | term * (ws*S('+-') *ws* term)**0

  # shift_expr: arith_expr (('<<'|'>>') arith_expr)*
  shift_expr = 'shift_expr' | arith_expr * (ws*(P('<<') + P('>>')) *ws* arith_expr)**0

  # and_expr: shift_expr ('&' shift_expr)*
  and_expr = 'and_expr' | shift_expr * (ws*'&' *ws* shift_expr)**0

  # xor_expr: and_expr ('^' and_expr)*
  xor_expr = 'xor_expr' | and_expr * (ws*'^' *ws* and_expr)**0

  # expr: xor_expr ('|' xor_expr)*
  expr = 'expr' | xor_expr * (ws*'|' *ws* xor_expr)**0

  # exprlist: expr (',' expr)* [',']
  exprlist = 'exprlist' | expr * (ws*',' *ws* expr)**0 * P(',')**-1

  # file_input: (NEWLINE | stmt)* ENDMARKER
  file_input = 'file_input' | (ws*newline + ws*stmt)**0

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
  setVs(funcdef,       [suite])
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

  return file_input

pygrammar = PythonGrammar()
#pygrammar.debug("named")

m = pygrammar.match("""
def test(one, two="none"):
  a = 5 and 2
  print "Stuff"

  if a:
    print "Got %s" % a
more
""")


print m