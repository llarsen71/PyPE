from behave import given, when, then
from PyLPEG.PyLPEG import P, S, R, SOL, EOL, Match
from hamcrest import assert_that, equal_to, none, not_none

# ******************************************************************************
# Given
# ******************************************************************************
# ==============================================================================
@given("p = {pattern} [{desc}]")
def step_impl(context, pattern, desc):
  context.p = eval(pattern)

# ******************************************************************************
# When
# ******************************************************************************
@when("p.match('{text}',{index}) is called")
def step_impl(context, text, index):
  # Convert escaped values in text to the unescaped value
  text = text.decode('string-escape')
  context.match = context.p.match(text, int(index))
  pass

# ******************************************************************************
# Then
# ******************************************************************************
@Then("the result is a match")
def step_impl(context):
  assert isinstance(context.match, Match)

# ==============================================================================
@then("the result fails because {reason}")
def step_impl(context, reason):
  pass

# ==============================================================================
@then("the result should be None")
def step_impl(context):
  assert_that(context.match, none())

# ==============================================================================
@then("match.start should be {index}")
def step_impl(context, index):
  assert_that(context.match, not_none())
  assert_that(context.match.start, equal_to(int(index)))

# ==============================================================================
@then("match.end should be {end}")
def step_impl(context, end):
  assert_that(context.match, not_none())
  assert_that(context.match.end, equal_to(int(end)))

# ==============================================================================
@then("str(match) should be '{match}'")
def step_impl(context, match):
  #if match == "''": match = ""
  assert_that(str(context.match), equal_to(match))

# ==============================================================================
@then("str(match) should be ''")
def step_impl(context):
  assert_that(str(context.match), equal_to(''))

# ==============================================================================
@then('repr(pattern) should be {pattern}')
def step_impl(context, pattern):
  assert_that(repr(context.p), equal_to(pattern))
