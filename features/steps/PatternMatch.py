from behave import given, when, then
from PyLPEG.PyLPEG import P, S, R, SOL
from hamcrest import assert_that, equal_to

#===============================================================================
@given("a pattern p = {cls}({pattern}) [{desc}]")
def step_impl(context, cls, pattern, desc):
  context.pattern = pattern
  if pattern.startswith("'") or pattern.startswith('"'):
    pattern = pattern[1:-1]
  elif pattern in ('True', 'False'):
    pattern = bool(pattern)
  else:
    pattern = int(pattern)
  classes = {'P':P, 'S':S, 'R': R}
  PtnCls = classes[cls]
  context.p = PtnCls(pattern)

#===============================================================================
@given("p = SOL() [Start of line pattern]")
def step_impl(context):
  context.p = SOL()

#===============================================================================
@when("p.match('{text}',{index}) is called")
def step_impl(context, text, index):
  context.match = context.p.match(text, int(index))
  pass

#===============================================================================
@when("the result is a match")
def step_impl(context):
  pass

#===============================================================================
@when("the result fails")
def step_impl(context):
  pass

#===============================================================================
@then("the result should be None")
def step_impl(context):
  assert context.match is None

#===============================================================================
@then("match.start should be {index}")
def step_impl(context, index):
  assert_that(context.match.start, equal_to(int(index)))

#===============================================================================
@then("match.end should be {end}")
def step_impl(context, end):
  assert_that(context.match.end, equal_to(int(end)))

#===============================================================================
@then("str(match) should be '{match}'")
def step_impl(context, match):
  if match == "''": match = ""
  assert_that(str(context.match), equal_to(match))

#===============================================================================
@then("str(match) should be ''")
def step_impl(context):
  assert_that(str(context.match), equal_to(''))

#===============================================================================
@then('repr(match) should be {cls}({pattern})')
def step_impl(context, cls, pattern):
  assert_that(repr(context.p), equal_to("{0}({1})".format(cls, pattern)))

@then('repr(match) should be SOL()')
def step_impl(context):
  assert_that(repr(context.p), equal_to("SOL()"))
