from behave import given, when, then
from PyLPEG.PyLPEG import P, S, R, SOL, whitespace0, newline
from PyLPEG.Tokenizer import Tokenizer
from hamcrest import assert_that, equal_to, none, not_none

ws          = whitespace0
rest_of_line = (1-newline)**0 * newline

# ******************************************************************************
# Given
# ******************************************************************************
@given("a Tokenizer T initialized with table")
def step_impl(context):
  if not context.table.has_column('grammar'):
    pattern = lambda row: eval(row["pattern"].replace("!","|"))
    rules = [pattern(row) for row in context.table]
    context.T = Tokenizer(root=rules)
  else:
    # Get the set of unique grammar names in the table.
    grammar_names = set(row['grammar'] for row in context.table)

    def pattern(row):
      pattern = eval(row["pattern"].replace("!", "|"))

      # return pattern if it does not start a new grammar
      if row['end pattern'] == "": return pattern

      # If this starts a new grammar, return:
      #    (pattern, new grammar name, end pattern)
      end_pattern = eval(row['end pattern'].replace('!','|'))

      return (pattern, row['new grammar'], end_pattern)

    rules = lambda grammar: [pattern(row) for row in context.table
                             if row['grammar'] == grammar]

    # For each of the unique grammar names, assemble the grammar rules and add
    # to .
    grammars = {grammar: rules(grammar) for grammar in grammar_names}
    context.T = Tokenizer(**grammars)

# ******************************************************************************
# When
# ******************************************************************************
@when("Tokenizer T.getTokens(text) is called with")
def step_impl(context):
  context.getTokens = context.T.getTokens(context.text)

# ******************************************************************************
# Then
# ******************************************************************************
@then("the tokens are")
def step_impl(context):
  rows = context.table.rows
  for i, (name, value) in enumerate(context.getTokens):
    # Check that we are in the expected grammar
    if context.table.has_column('grammar'):
      grammar = context.T.currentGrammarName()
      assert_that(grammar, equal_to(rows[i]['grammar']))

    # Verify the token name
    assert_that(name, equal_to(rows[i]['name']))

    # Verify the value
    val = str(value).replace("\r\n","\n").replace("\r","\n")
    expected = rows[i]['value'].decode('string-escape')
    assert_that(val, equal_to(expected))
