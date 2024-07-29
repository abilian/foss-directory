from typing import List

from devtools import debug
from jinja2 import Environment, PackageLoader, select_autoescape
from jinja2.nodes import For, Name
from jinja2.parser import Parser

env = Environment()

# template = env.get_template("security/base.html")

# language=html
TEMPLATE = """
<h1>Test</h1>

{% for x in [1,2,3] %}
{{ x }}
{% endfor %}
"""

parser = Parser(env, TEMPLATE)
t = parser.parse()
# debug(t)

body = t.body
# debug(body)

# debug(body[0])
# debug(body[1])
for_ = body[1]
# debug(for_.target.name)


def unparse(n):
    match n:
        case [*nodes]:
            for node in nodes:
                unparse(node)

        case For():
            print("target: ", end="")
            unparse(n.target)
            print()

            print("iter:", end="")
            unparse(n.iter)
            print()

            print("body:", end="")
            unparse(n.body)
            print()

        case Name():
            return n.name

unparse(for_)
