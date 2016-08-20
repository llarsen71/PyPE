Feature: Basic pattern match operations should be defined in order to make it
  relatively easy to construct a text parser.

Scenario Outline: Match a specific string.
  Given a pattern p = P('<text>')
  When p.match('<string>',<index>) is called
  and the result is a match
  Then match.start should be <index>
  And match.end should be <end>
  And str(match) should be '<text>'
  And repr(match) should be P("<text>")

  Examples:
    | string              | isMatch     | text | index | end |
    | Blue flying monkeys | a match     | Blue | 0     | 4   |
    | Blue flying monkeys | not a match | fly  | 5     | 8   |
