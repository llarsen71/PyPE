Feature: The Tokenizer is used to parse a file using one or more grammars.
  The following patterns are defined
    ws           = whitespace0
    rest_of_line = (1 - newline)**0 * newline
#-------------------------------------------------------------------------------
Scenario: Parse lines starting with fortran comment marker.
  Given a Tokenizer T initialized with table
    | name    | pattern             |
    | comment | ws*'!'*rest_of_line |
    | line    | rest_of_line        |
  When  Tokenizer T.getTokens(text) is called with
    """
    First line
    ! Comment line
    Third line
    ! Last line
    """
  Then  the tokens are
    | name    | value            |
    | line    | First line\n     |
    | comment | ! Comment line\n |
    | line    | Third line\n     |
    | comment | ! Last line\n    |

#-------------------------------------------------------------------------------
Scenario: Parse lines starting with fortran comment marker.
  Given a Tokenizer T initialized with table
    | grammar | name    | pattern                | new grammar | end pattern |
    | root    | line    | rest_of_line - S('!*') |             |             |
    | root    | <cmnt>  | ~S('!*')               | cmnt1       | -S('!*')    |
    | cmnt1   | cmnt!   | S('!') * rest_of_line  |             |             |
    | cmnt1   | <cmnt>  | ~S('*')                | cmnt2       | -P('*')     |
    | cmnt2   | cmnt*   | S('*') * rest_of_line  |             |             |
  When  Tokenizer T.getTokens(text) is called with
    """
    First line
    * comment
    ! test
    ! next
    Last line
    """
  Then  the tokens are
    | name       | value         | grammar |
    | line       | First line\n  | root    |
    | <cmnt>     |               | root    |
    | <cmnt>     |               | cmnt1   |
    | cmnt*      | * comment\n   | cmnt2   |
    | <end cmnt> |               | cmnt2   |
    | cmnt!      | ! test\n      | cmnt1   |
    | cmnt!      | ! next\n      | cmnt1   |
    | <end cmnt> |               | cmnt1   |
    | line       | Last line\n   | root    |
