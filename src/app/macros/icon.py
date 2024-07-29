import re

from markupsafe import Markup
from pagic.macros import macro


@macro
def icon(name, type="solid", **kw):
    body = open(f"icons/{type}/{name}.svg").read()

    if "_class" in kw:
        kw["class"] = kw["_class"]
        del kw["_class"]

    if kw:
        attrs_list = []
        for attr_name, attr_value in kw.items():
            attr_name = attr_name.replace("_", "-")
            attrs_list.append(f"{attr_name}='{attr_value}'")
        attrs = " ".join(attrs_list)
        body = re.sub("<svg ", f"<svg {attrs} ", body)

    return Markup(body)
