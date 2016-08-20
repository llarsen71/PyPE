from behave import given, when, then
from PyLPEG import P
from hamcrest import assert_that, equal_to

#===============================================================================
@given("a pattern p = P('{string}')")
def step_impl(context, string):
  context.p = P(string)

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
@then("match.start should be {index}")
def step_impl(context, index):
  assert_that(context.match.start, equal_to(int(index)))

#===============================================================================
@then("match.end should be {end}")
def step_impl(context, end):
  assert_that(context.match.end, equal_to(int(end)))

#===============================================================================
@then("str(match) should be '{text}'")
def step_impl(context, text):
  assert_that(str(context.match), equal_to(text))

#===============================================================================
@then('repr(match) should be P("{string}")')
def step_impl(context, string):
  assert_that(repr(context.p), equal_to("P('{0}')".format(string)))