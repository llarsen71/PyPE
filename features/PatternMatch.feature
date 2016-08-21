Feature: Basic pattern match operations should be defined in order to make it
  relatively easy to construct a text parser.

Scenario Outline: Match a simple pattern.
  Given a pattern p = <cls>(<pattern>) [<desc>]
  When p.match('<string>',<index>) is called
  and the result is a match
  Then match.start should be <index>
  And match.end should be <end>
  And str(match) should be '<match>'
  And repr(match) should be <cls>(<pattern>)

  Examples:
    | string              | cls | pattern | index | end | match | desc                         |
    | Blue flying monkeys | P   | 'Blue'  | 0     | 4   | Blue  | match string                 |
    | Blue flying monkeys | P   | 'fly'   | 5     | 8   | fly   | match string                 |
    | Blue flying monkeys | P   | 4       | 12    | 16  | monk  | match 4 characters           |
    | Blue flying monkeys | P   | -5      | 15    | 19  | keys  | match less than 5 characters |
    | Blue flying monkeys | P   | True    | 3     | 3   |       | always match                 |
    | Blue flying monkeys | R   | 'az'    | 12    | 13  | m     | match range                  |
    | Blue flying monkeys | S   | 'Bs'    | 0     | 1   | B     | match character in set       |
    | Blue flying monkeys | S   | 'Bs'    | 18    | 19  | s     | match character in set       |

Scenario Outline: A simple pattern fails.
  Given a pattern p = <cls>(<pattern>) [<desc>]
  When p.match('<string>',<index>) is called
  and the result fails
  Then the result should be None

  Examples:
    | string              | cls | pattern | index | desc                         |
    | Blue flying monkeys | P   | 'Blue'  | 2     | match string                 |
    | Blue flying monkeys | P   | 4       | 20    | match 4 characters           |
    | Blue flying monkeys | P   | -5      | 12    | match less than 5 characters |
    | Blue flying monkeys | R   | 'az'    | 0     | match range                  |
    | Blue flying monkeys | S   | 'Bs'    | 1     | match character in set       |


Scenario Outline: Match the start of a line
  Given p = SOL() [Start of line pattern]
  When p.match('<string>',<index>) is called
  and the result is a match
  Then match.start should be <index>
  And match.end should be <end>
  And str(match) should be ''
  And repr(match) should be SOL()

  Examples:
    | string    | index | end | match | desc                         |
    | 1\n2\n3\n | 0     | 0   | Blue  | match string                 |
