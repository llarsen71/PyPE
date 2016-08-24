Feature: The Tokenizer is used to parse a file using one or more grammars.
  The following patterns are defined
    ws           = whitespace0
    rest_of_line = (1 - newline)**0 * newline
#-------------------------------------------------------------------------------
Scenario: Parse lines starting with fortran comment marker. Use '!' for pipe '|'
  in tables until pipe is supported in tables. 
  Given a Tokenizer T initialized with table
    |             pattern             |
    | 'comment' ! ws*'#'*rest_of_line |
    | 'line'    ! rest_of_line        |
  When  Tokenizer T.getTokens(text) is called with
    """
    First line
    # Comment line
    Third line
    # Last line
    """
  Then  the tokens are
    | name    | value            |
    | line    | First line\n     |
    | comment | # Comment line\n |
    | line    | Third line\n     |
    | comment | # Last line\n    |

#-------------------------------------------------------------------------------
Scenario: Parse lines starting with fortran comment marker. Use '!' for pipe '|'
  in tables until pipe is supported in tables. 
  Given a Tokenizer T initialized with table
    | grammar |              pattern              | new grammar |    end pattern      |
    | root    | 'line'   ! rest_of_line - S('#*') |             |                     |
    | root    | '+cmnt#' ! ~S('#*')               | CMNT#       | '-cmnt#' ! -S('#*') |
    | CMNT#   | 'cmnt#'  ! S('#') * rest_of_line  |             |                     |
    | CMNT#   | '+cmnt*' ! ~S('*')                | CMNT*       | '-cmnt*' ! -P('*')  |
    | CMNT*   | 'cmnt*'  ! S('*') * rest_of_line  |             |                     |
  When  Tokenizer T.getTokens(text) is called with
    """
    First line
    * comment
    # test
    # next
    Last line
    """
  Then  the tokens are
    | name       | value         | grammar |
    | line       | First line\n  | root    |
    | +cmnt#     |               | root    |
    | +cmnt*     |               | CMNT#   |
    | cmnt*      | * comment\n   | CMNT*   |
    | -cmnt*     |               | CMNT*   |
    | cmnt#      | # test\n      | CMNT#   |
    | cmnt#      | # next\n      | CMNT#   |
    | -cmnt#     |               | CMNT#   |
    | line       | Last line\n   | root    |
