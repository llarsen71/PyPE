from PyPE import P, S, R, C, Cc, Cb, Cg, SOL, EOL, \
                 whitespace1 as ws1, whitespace0 as ws, \
                 alpha, digit, newline, quote, V, setVs

# ==============================================================================
def NAME_():
  return  "name" | (alpha + '_') * (alpha + digit + '_')**0 & 'hide'

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

  integer        = decimalinteger + octinteger + hexinteger + bininteger
  longinteger    = integer * S("lL")

  # ----------------------------------------------------------------------------
  # floating point numbers
  # ----------------------------------------------------------------------------
  exponent      = S("eE") * S("+-")**-1 * digit**1
  fraction      = "." * digit**1
  intpart       = digit**1
  pointfloat    = (intpart**-1 * fraction) + (intpart * ".")
  exponentfloat = (intpart + pointfloat) * exponent
  floatnumber   = pointfloat + exponentfloat

  # ----------------------------------------------------------------------------
  # imaginary number
  # ----------------------------------------------------------------------------
  imagnumber = (floatnumber + intpart) * S("jJ")

  # ----------------------------------------------------------------------------
  # numbers
  # ----------------------------------------------------------------------------
  return "number" | integer + longinteger + floatnumber + imagnumber & "hide"

# ==============================================================================
def STRING():
  escapeseq       = "\\" * P(1)
  longstringchar  = P(1) - "\\"
  shortstringchar = P(1) - ("\\" + newline + quote)
  longstringitem  = longstringchar + escapeseq
  shortstringitem = shortstringchar + escapeseq

  longstring      = ("'''" * longstringitem**0 * "'''" +
                     '"""' * longstringitem**0 * '"""')
  shortstring     = Cb("quote",quote) * shortstringitem**0 * Cb("quote")

  stringprefix    =  S("rR") + S("uUbB") * S("rR")**-1
  stringliteral   =  stringprefix**-1 * (shortstring + longstring)

  return "string" | longstring + shortstring + stringliteral & "hide"

# ==============================================================================
def PythonGrammar():
  NAME = NAME_()

  # file_input: (NEWLINE | stmt)* ENDMARKER
  file_input = (ws*newline + ws*V('stmt'))**0

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
  augassign = P('+=') + P('-=') + P('*=') + P('/=') + P('%=') + P('&=') + P('|=') + \
              P('^=') + P('<<=') + P('>>=') + P('**=') + P('//=')

  # ----------------------------------------------------------------------------
  # Simple Statement
  # ----------------------------------------------------------------------------

  # expr_stmt: testlist (augassign (yield_expr|testlist) |
  #                      ('=' (yield_expr|testlist))*)
  expr_stmt = 'expr_stmt' | V('testlist') * (ws*augassign*ws* (V('yield_expr')+V('testlist')) +
                               (ws*'='*ws*(V('yield_expr')+V('testlist')))**0)

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

  # import_name: 'import' dotted_as_names
  import_name = 'import_name' | 'import' *ws1* V('dotted_as_names')

  # import_as_name: NAME ['as' NAME]
  import_as_name = NAME * (ws1*'as'*ws1*NAME)**-1

  # import_as_names: import_as_name (',' import_as_name)* [',']
  import_as_names = import_as_name * (ws*','*import_as_name)**0 * (ws*P(','))**-1

  # import_from: ('from' ('.'* dotted_name | '.'+)
  #               'import' ('*' | '(' import_as_names ')' | import_as_names))
  import_from = 'from' *ws1* (P('.')**0*V('dotted_name') + P('.')**1) *ws* \
                'import' * (ws*'*' + '('*ws*import_as_name*ws*')' )

  # import_stmt: import_name | import_from
  import_stmt = import_name + import_from

  # global_stmt: 'global' NAME (',' NAME)*
  global_stmt = 'global'*ws1*NAME*(ws*','*ws*NAME)**0

  # exec_stmt: 'exec' expr ['in' test [',' test]]
  exec_stmt = 'exec'*ws1*V('expr')*(ws1*'in'*V('test') * (ws*','*ws*V('test'))**-1)**-1

  # assert_stmt: 'assert' test [',' test]
  assert_stmt = 'assert'*ws1*V('test') * (ws*','*V('test'))**-1

  # small_stmt: (expr_stmt | print_stmt  | del_stmt | pass_stmt | flow_stmt |
  #              import_stmt | global_stmt | exec_stmt | assert_stmt)
  small_stmt = 'small_stmt' | expr_stmt + print_stmt + del_stmt + pass_stmt + \
               flow_stmt + import_stmt + global_stmt + exec_stmt + assert_stmt

  # simple_stmt: small_stmt (';' small_stmt)* [';'] NEWLINE
  simple_stmt = 'simple_stmt' | small_stmt * (ws*';'*ws*small_stmt)**0 * (ws*P(';'))**-1 *ws* (newline)**-1

  # ----------------------------------------------------------------------------
  # Compound Statement
  # ----------------------------------------------------------------------------
  # TODO: Track the indentation and unindent
  INDENT = ws
  DEDENT = ws

  # suite: simple_stmt | NEWLINE INDENT stmt+ DEDENT
  suite = simple_stmt + ws* newline * INDENT * V('stmt')**1 * DEDENT

  # if_stmt: 'if' test ':' suite ('elif' test ':' suite)* ['else' ':' suite]
  if_stmt = 'if_stmt' | 'if'*ws*V('test')*ws*':'*suite

  # while_stmt: 'while' test ':' suite ['else' ':' suite]
  suite_else =  suite * ('else'*ws*':'*suite)**-1
  while_stmt = 'while_stmt' | 'while' *ws1* V('test')*ws*':' * suite_else

  # for_stmt: 'for' exprlist 'in' testlist ':' suite ['else' ':' suite]
  for_stmt = 'for_stmt' | 'for' *ws1* V('exprlist') *ws1* 'in' *ws1* V('testlist')*ws*':' * suite_else

  # # NB compile.c makes sure that the default except clause is last
  # except_clause: 'except' [test [('as' | ',') test]]
  except_clause = 'except' * (ws1* V('test') * ((ws1*'as'*ws1 + ws*','*ws)*V('test'))**-1)**-1

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
  with_item = V('test') * (ws1*'as'*ws1*V('expr'))**-1

  # with_stmt: 'with' with_item (',' with_item)*  ':' suite
  with_stmt = 'with_stmt' | 'with' *ws1* with_item *(ws*','*ws*with_item)**0 *ws*':' * suite

  # dotted_name: NAME ('.' NAME)*
  dotted_name = NAME * ("." * NAME)**0

  # dotted_as_name: dotted_name ['as' NAME]
  dotted_as_name = dotted_name * (ws1*'as'*ws1*NAME)**-1

  # dotted_as_names: dotted_as_name (',' dotted_as_name)*
  dotted_as_names = dotted_as_name * (ws* ',' *ws* dotted_as_name)**0

  # # The reason that keywords are test nodes instead of NAME is that using NAME
  # # results in an ambiguity. ast.c makes sure it's a NAME.
  # argument: test [comp_for] | test '=' test
  argument = V('test') *ws* (V('comp_for'))**-1 + V('test') *ws*'='*ws* V('test')

  # arglist: (argument ',')* (argument [',']
  #                          |'*' test (',' argument)* [',' '**' test]
  #                          |'**' test)
  arglist = (argument*ws*',')**0 * (argument * (ws*',')**-1 +
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
  testlist = V('test') * (ws*','*ws*V('test'))**0 * (ws*',')**-1

  # classdef: 'class' NAME ['(' [testlist] ')'] ':' suite
  classdef = 'classdef' | 'class' *ws1* NAME * ('('*ws*testlist*ws*')')**-1 * ':' *suite

  # decorated: decorators (classdef | funcdef)
  decorated = 'decorated' | decorators * (classdef + funcdef)

  # compound_stmt: if_stmt | while_stmt | for_stmt | try_stmt | with_stmt | funcdef | classdef | decorated
  compound_stmt = if_stmt + while_stmt + for_stmt + try_stmt + with_stmt + funcdef + classdef + decorated

  # ----------------------------------------------------------------------------
  # Statement
  # ----------------------------------------------------------------------------

  # stmt: simple_stmt | compound_stmt
  stmt = 'stmt' | simple_stmt + compound_stmt

  # ----------------------------------------------------------------------------
  # Comparison
  # ----------------------------------------------------------------------------

  # comp_op: '<'|'>'|'=='|'>='|'<='|'<>'|'!='|'in'|'not' 'in'|'is'|'is' 'not'
  comp_op = P('<') + P('>') + P('==') + P('>=') + P('<=') + P('<>') + P('!=') + \
            P('in') + P('not')*ws1*P('in') + P('is') + P('is')*ws1*P('not')

  # comparison: expr (comp_op expr)*
  comparison = V('expr') * (ws*comp_op*ws*V('expr'))**0

  # not_test: 'not' not_test | comparison
  not_test = ('not'*ws1)**0  * comparison

  # and_test: not_test ('and' not_test)*
  and_test = not_test * (ws1*'and'*ws1* not_test)**0

  # or_test: and_test ('or' and_test)*
  or_test = and_test * (ws1*'or'*ws1 * and_test)**0

  # # Backward compatibility cruft to support:
  # # [ x for x in lambda: True, lambda: False if x() ]
  # # even while also allowing:
  # # lambda x: 5 if x else 2
  # # (But not a mix of the two)
  # old_lambdef: 'lambda' [varargslist] ':' old_test
  old_lambdadef = 'lambda' *ws1* (varargslist)**-1 *ws*':' * V('old_test')

  # old_test: or_test | old_lambdef
  # testlist_safe: old_test [(',' old_test)+ [',']]

  # comp_for: 'for' exprlist 'in' or_test [comp_iter]
  comp_for = 'comp_for' | 'for' *ws1* V('exprlist') *ws1* 'in' *ws1* or_test * (V('comp_iter')**-1

  # comp_if: 'if' old_test [comp_iter]
  comp_if = 'if' * ws1 * old_test * (V('comp_iter')) ** -1

  # comp_iter: comp_for | comp_if
  comp_iter = 'comp_iter' | comp_for + comp_if

  # ----------------------------------------------------------------------------
  # Test
  # ----------------------------------------------------------------------------

  # lambdef: 'lambda' [varargslist] ':' test
  lambdadef = 'lambda' *ws1* (varargslist)**-1 *ws*':' * V('test')

  # test: or_test ['if' or_test 'else' test] | lambdef

  # ----------------------------------------------------------------------------
  # Atom
  # ----------------------------------------------------------------------------

  # dictorsetmaker: ( (test ':' test (comp_for | (',' test ':' test)* [','])) |
  #                   (test (comp_for | (',' test)* [','])) )
  # list_for: 'for' exprlist 'in' testlist_safe [list_iter]
  # list_if: 'if' old_test [list_iter]
  # list_iter: list_for | list_if
  # listmaker: test ( list_for | (',' test)* [','] )
  # testlist_comp: test ( comp_for | (',' test)* [','] )
  # yield_expr: 'yield' [testlist]
  # testlist1: test (',' test)*
  # atom: ('(' [yield_expr|testlist_comp] ')' |
  #        '[' [listmaker] ']' |
  #        '{' [dictorsetmaker] '}' |
  #        '`' testlist1 '`' |
  #        NAME | NUMBER | STRING+)

  # ----------------------------------------------------------------------------
  # Term
  # ----------------------------------------------------------------------------

  # sliceop: ':' [test]
  # subscript: '.' '.' '.' | test | [test] ':' [test] [sliceop]
  # subscriptlist: subscript (',' subscript)* [',']
  # trailer: '(' [arglist] ')' | '[' subscriptlist ']' | '.' NAME
  # power: atom trailer* ['**' factor]
  # factor: ('+'|'-'|'~') factor | power
  # term: factor (('*'|'/'|'%'|'//') factor)*

  # ----------------------------------------------------------------------------
  # Expression
  # ----------------------------------------------------------------------------

  # arith_expr: term (('+'|'-') term)*
  # shift_expr: arith_expr (('<<'|'>>') arith_expr)*
  # and_expr: shift_expr ('&' shift_expr)*
  # xor_expr: and_expr ('^' and_expr)*
  # expr: xor_expr ('|' xor_expr)*
  # exprlist: expr (',' expr)* [',']

  setVs(fpdef, [fplist])

PythonGrammar()
