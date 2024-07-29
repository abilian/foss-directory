import pytest

from splinter import Browser

from app.main import create_app


@pytest.mark.skip
# Not working currently because version conflicts
# Need to install 'splinter[flask]' without conflicting w/ behaving first.
def test_home():
    app = create_app()
    browser = Browser("flask", app=app)
    browser.visit("/")
