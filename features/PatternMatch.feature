Feature: Basic pattern match operations should be defined in order to make it
  relatively easy to construct basic matching patterns.

#-------------------------------------------------------------------------------
Scenario Outline: Match a simple pattern.
  Given p = <pattern> [<desc>]
  When  p.match('<string>',<index>) is called
  Then  the result is a match
  And   match.start should be <start>
  And   match.end should be <end>
  And   str(match) should be '<match>'
  And   repr(pattern) should be <pattern>

  Examples:
    | pattern    | desc                         | string              | index | start | end | match |
    | P('Blue')  | match string                 | Blue flying monkeys | 0     | 0     | 4   | Blue  |
    | P('fly')   | match string                 | Blue flying monkeys | 5     | 5     | 8   | fly   |
    | P(4)       | match 4 characters           | Blue flying monkeys | 12    | 12    | 16  | monk  |
    | P(-5)      | match less than 5 characters | Blue flying monkeys | 15    | 15    | 19  | keys  |
    | P(True)    | always match                 | Blue flying monkeys | 3     | 3     | 3   |       |
    | R('az')    | match range                  | Blue flying monkeys | 12    | 12    | 13  | m     |
    | S('Bs')    | match character in set       | Blue flying monkeys | 0     | 0     | 1   | B     |
    | S('Bs')    | match character in set       | Blue flying monkeys | -1    | 18    | 19  | s     |

#-------------------------------------------------------------------------------
Scenario Outline: A simple pattern fails.
  Given p = <pattern> [<desc>]
  When  p.match('<string>',<index>) is called
  Then  the result fails because <reason>
  And   the result should be None

  Examples:
    | pattern   | desc                         | string              | index | reason                         |
    | P('Blue') | match string                 | Blue flying monkeys | 2     | Blue starts at 0 not 2         |
    | P(4)      | match 4 characters           | Blue flying monkeys | 18    | less than 4 chars remain at 18 |
    | P(-5)     | match less than 5 characters | Blue flying monkeys | -6    | more than 4 chars remain       |
    | R('az')   | match range                  | Blue flying monkeys | 0     | B (index 0) is not lower case  |
    | S('Bs')   | match character in set       | Blue flying monkeys | 2     | u (index 2) not in set Bs      |

#-------------------------------------------------------------------------------
Scenario Outline: Match start of line (SOL) or end of line (EOL)
  Given p = <pattern> [<desc>]
  When  p.match('<string>',<index>) is called
  Then  the result is a match
  And   match.start should be <index>
  And   match.end should be <index>
  And   str(match) should be ''
  And   repr(pattern) should be <pattern>

  Examples:
    | pattern | desc          | string    | index |
    | SOL()   | Start Of Line | 1\n2\n3\r | 0     |
    | SOL()   | Start Of Line | 1\n2\n3\r | 2     |
    | SOL()   | Start Of Line | 1\n2\n3\r | 6     |
    | EOL()   | End of Line   | 1\n2\n3\n | 1     |
    | EOL()   | End of Line   | 1\n2\n3\n | 3     |
    | EOL()   | End of Line   | 1\n2\n3\n | 6     |

#-------------------------------------------------------------------------------
Scenario Outline: Start of a line (SOL) or end of line (EOL) fails
  Given p = <pattern> [<desc>]
  When  p.match('<string>',<index>) is called
  Then  the result fails because <reason>
  And   the result should be None

  Examples:
    | pattern | desc          | string     | index | reason                     |
    | SOL()   | Start Of Line | 1\n2\n3\n  | 1     | index not at start of line |
    | SOL()   | Start Of Line | 1\n2\n3\n4 | 7     | index not at start of line |
    | EOL()   | End Of Line   | 1\n2\n3\n  | 0     | index not at end of line   |
    | EOL()   | End Of Line   | 1\n2\n3\n4 | 6     | index not at end of line   |

#-------------------------------------------------------------------------------
Scenario Outline: Match a pattern1, or if that fails, pattern2.
  (i.e., pattern1 + pattern2).
  Given p = <pattern> [<desc>]
  When  p.match('<string>',<index>) is called
  Then  the result is a match
  And   match.start should be <index>
  And   match.end should be <end>
  And   str(match) should be '<match>'
  And   repr(pattern) should be <pattern>

  Examples:
    | pattern                   | desc                 | string       | index | end | match  |
    | P('peanut') + P('butter') | 'peanut' or 'butter' | peanutbutter | 0     | 6   | peanut |
    | P('peanut') + P('butter') | 'peanut' or 'butter' | peanutbutter | 6     | 12  | butter |

#-------------------------------------------------------------------------------
Scenario Outline: Match pattern1 if it does not match pattern2.
  (i.e., pattern1 - pattern2).
  Given p = <pattern> [<desc>]
  When  p.match('<string>',<index>) is called
  Then  the result is a match
  And   match.start should be <index>
  And   match.end should be <end>
  And   str(match) should be '<match>'
  And   repr(pattern) should be <pattern>

  Examples:
    | pattern          | desc         | string       | index | end | match  |
    | P(6) - P('tea')  | p1 if not p2 | peanutbutter | 0     | 6   | peanut |
    | P(6) - P('batt') | p1 if not p2 | peanutbutter | 6     | 12  | butter |

#-------------------------------------------------------------------------------
Scenario Outline: Match pattern1 if it does not match pattern2.
  (i.e., pattern1 - pattern2).
  Given p = <pattern> [<desc>]
  When  p.match('<string>',<index>) is called
  Then  the result fails because <reason>
  And   the result should be None

  Examples:
    | pattern         | desc         | string       | index | reason                    |
    | P(6) - P('p')   | p1 if not p2 | peanutbutter | 0     | 'p' at 0 is not allowed   |
    | P(6) - P('but') | p1 if not p2 | peanutbutter | 6     | 'but' at 6 is not allowed |

#-------------------------------------------------------------------------------
Scenario Outline: Match if not pattern.
  (i.e., -pattern).
  Given p = <pattern> [<desc>]
  When  p.match('<string>',<index>) is called
  Then  the result is a match
  And   match.start should be <index>
  And   match.end should be <index>
  And   str(match) should be ''
  And   repr(pattern) should be <pattern>

  Examples:
    | pattern     | desc     | string | index |
    | -P('Will')  | not Will | Halt   | 0     |
    | -P('Will')  | not Will | Erak   | 0     |

#-------------------------------------------------------------------------------
Scenario Outline: Match if not pattern.
  (i.e., -pattern).
  Given p = <pattern> [<desc>]
  When  p.match('<string>',<index>) is called
  Then  the result fails because <reason>
  And   the result should be None

  Examples:
    | pattern     | desc     | string | index | reason                  |
    | -P('Will')  | not Will | Will   | 0     | string starts with Will |
    | -P('Will')  | not Will | Willow | 0     | string starts with Will |

#-------------------------------------------------------------------------------
Scenario Outline: Match a pattern repeating n or more times (pattern^n) or
  up to n times (pattern^-n).
  Given p = <pattern> [<desc>]
  When  p.match('<string>',<index>) is called
  Then  the result is a match
  And   match.start should be <index>
  And   match.end should be <end>
  And   str(match) should be '<result>'
  And   repr(pattern) should be <pattern>

  Examples:
    | pattern   | desc           | string | index | end | result |
    | P('a')**0 | 0 or more a(s) | b      | 0     | 0   |        |
    | P('a')**0 | 0 or more a(s) | aab    | 0     | 2   | aa     |
    | P('a')**3 | 3 or more a(s) | aaab   | 0     | 3   | aaa    |
    | P('a')**3 | 3 or more a(s) | aaaaab | 0     | 5   | aaaaa  |
