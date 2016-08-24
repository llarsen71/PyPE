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
  if 'grammar' not in context.table:
    rules = [eval(row["pattern"]) | row['name'] for row in context.table]
    context.T = Tokenizer(root=rules)
  else:
    grammar_names = set(row['grammar'] for row in context.table)
    def pattern(row):
      pattern = eval(row['pattern'])
    rules = lambda grammar: [eval(row["pattern"]) | row['name'] for row in context.table if row['grammar'] == grammar ]
    grammars = {grammar: rules(grammar) for grammar in grammar_names }
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
    assert_that(rows[i]['name'], equal_to(name))
    val = str(value).replace("\r\n","\n").replace("\r","\n")
    assert_that(rows[i]['value'].decode('string-escape'), equal_to(val))
