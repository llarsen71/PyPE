from behave import given, when, then
from PyLPEG.PyLPEG import P, S, R, SOL
from hamcrest import assert_that, equal_to, none, not_none

# ==============================================================================
def massagePattern(pattern):
  if pattern.startswith("'") or pattern.startswith('"'): return pattern[1:-1]
  if pattern in ('True', 'False'):return bool(pattern)
  return int(pattern)

# ******************************************************************************
# Given
# ******************************************************************************
@given("a pattern p = {cls}({pattern}) [{desc}]")
def step_impl(context, cls, pattern, desc):
  PtnCls = {'P':P, 'S':S, 'R': R}[cls]
  context.p = PtnCls(massagePattern(pattern))

# ==============================================================================
@given("p = SOL() [Start of line pattern]")
def step_impl(context):
  context.p = SOL()

# ==============================================================================
@given("p = P({pattern1})*P({pattern2})")
def step_impl(context, pattern1, pattern2):
  context.p = P(massagePattern(pattern1)) * P(massagePattern(pattern2))

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
  pass

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
@then('repr(match) should be: {cls}({pattern})')
def step_impl(context, cls, pattern):
  assert_that(repr(context.p), equal_to("{0}({1})".format(cls, pattern)))

# ==============================================================================
@then('repr(match) should be SOL()')
def step_impl(context):
  assert_that(repr(context.p), equal_to("SOL()"))

# ==============================================================================
@then('repr(match) should be P({pattern1})*P({pattern2})')
def step_impl(context, pattern1, pattern2):
  assert_that(repr(context.p), equal_to("P({0})*P({1})".format(pattern1, pattern2)))