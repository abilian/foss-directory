# ruff: noqa: F403

from behave import when
from behaving.mail.steps import *
from behaving.notifications.gcm.steps import *
from behaving.personas.steps import *
from behaving.sms.steps import *
from behaving.web.steps import *

HOME = "https://aipress24.demo.abilian.com/"


@when("I go to home")
def go_to_home(context):
    context.browser.visit(HOME)
