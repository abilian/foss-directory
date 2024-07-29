import time
from functools import wraps

from bs4 import BeautifulSoup
from lxml.html.clean import Cleaner


def html_to_text(html):
    html = html.strip()
    if html:
        try:
            cleaner = Cleaner(style=True)
            html = cleaner.clean_html(html)
        except:
            # TODO
            html = ""

    if html and html.startswith("<"):
        text = BeautifulSoup(html, features="lxml").text
    else:
        text = html

    return text


def timer(func):
    @wraps(func)
    def _time_it(*args, **kwargs):
        start = int(round(time.time() * 1000))
        try:
            return func(*args, **kwargs)
        finally:
            end_ = int(round(time.time() * 1000)) - start
            print(f"Total execution time: {end_ if end_ > 0 else 0} ms")

    return _time_it
