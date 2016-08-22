Feature: Basic pattern match operations should be defined in order to make it
  relatively easy to construct basic matching patterns.

Scenario Outline: Match a simple pattern.
  Given a pattern p = <cls>(<pattern>) [<desc>]
  When p.match('<string>',<index>) is called
  Then the result is a match
  And match.start should be <start>
  And match.end should be <end>
  And str(match) should be '<match>'
  And repr(match) should be: <cls>(<pattern>)

  Examples:
    | string              | cls | pattern | index | start | end | match | desc                         |
    | Blue flying monkeys | P   | 'Blue'  | 0     | 0     | 4   | Blue  | match string                 |
    | Blue flying monkeys | P   | 'fly'   | 5     | 5     | 8   | fly   | match string                 |
    | Blue flying monkeys | P   | 4       | 12    | 12    | 16  | monk  | match 4 characters           |
    | Blue flying monkeys | P   | -5      | 15    | 15    | 19  | keys  | match less than 5 characters |
    | Blue flying monkeys | P   | True    | 3     | 3     | 3   |       | always match                 |
    | Blue flying monkeys | R   | 'az'    | 12    | 12    | 13  | m     | match range                  |
    | Blue flying monkeys | S   | 'Bs'    | 0     | 0     | 1   | B     | match character in set       |
    | Blue flying monkeys | S   | 'Bs'    | -1    | 18    | 19  | s     | match character in set       |

Scenario Outline: A simple pattern fails.
  Given a pattern p = <cls>(<pattern>) [<desc>]
  When p.match('<string>',<index>) is called
  Then the result fails because <reason>
  And the result should be None

  Examples:
    | string              | cls | pattern | index | desc                         | reason                         |
    | Blue flying monkeys | P   | 'Blue'  | 2     | match string                 | Blue starts at 0 not 2         |
    | Blue flying monkeys | P   | 4       | 18    | match 4 characters           | less than 4 chars remain at 18 |
    | Blue flying monkeys | P   | -5      | -6    | match less than 5 characters | more than 4 chars remain       |
    | Blue flying monkeys | R   | 'az'    | 0     | match range                  | B (index 0) is not lower case  |
    | Blue flying monkeys | S   | 'Bs'    | 2     | match character in set       | u (index 2) not in set Bs      |

Scenario Outline: Match the start of a line
  Given p = SOL() [Start of line pattern]
  When p.match('<string>',<index>) is called
  Then the result is a match
  And match.start should be <index>
  And match.end should be <index>
  And str(match) should be ''
  And repr(match) should be SOL()

  Examples:
    | string    | index | end |
    | 1\n2\n3\r | 0     | 0   |
    | 1\n2\n3\r | 2     | 0   |
    | 1\n2\n3\r | 6     | 0   |

Scenario Outline: Match the start of a line fails
  Given p = SOL() [Start of line pattern]
  When p.match('<string>',<index>) is called
  Then the result fails because <reason>
  And the result should be None

  Examples:
    | string     | index | reason                     |
    | 1\n2\n3\n  | 1     | index not at start of line |
    | 1\n2\n3\n4 | 7     | index not at start of line |

Scenario Outline: Match the start of a line
  Given p = SOL() [Start of line pattern]
  When p.match('<string>',<index>) is called
  Then the result is a match
  And match.start should be <index>
  And match.end should be <index>
  And str(match) should be ''
  And repr(match) should be SOL()

  Examples:
    | string    | index | end |
    | 1\n2\n3\n | 0     | 0   |
    | 1\n2\n3\n | 2     | 0   |
    | 1\n2\n3\n | 6     | 0   |

Scenario Outline: Match the start of a line fails
  Given p = SOL() [Start of line pattern]
  When p.match('<string>',<index>) is called
  Then the result fails because <reason>
  And the result should be None

  Examples:
    | string     | index | reason                     |
    | 1\n2\n3\n  | 1     | index not at start of line |
    | 1\n2\n3\n4 | 7     | index not at start of line |

Scenario Outline: Match a pattern followed by another pattern
  (i.e., pattern1 * pattern2).
  Given p = P(<pattern1>)*P(<pattern2>)
  When p.match('<string>',<index>) is called
  Then the result is a match
  And match.start should be <index>
  And match.end should be <end>
  And str(match) should be '<match>'
  And repr(match) should be P(<pattern1>)*P(<pattern2>)

  Examples:
    | string       | pattern1 | pattern2 | index | end | match        |
    | peanutbutter | 'peanut' | 'butter' | 0     | 12  | peanutbutter |
    | peanutbutter | 'pea'    | 'nut'    | 0     | 6   | peanut       |
