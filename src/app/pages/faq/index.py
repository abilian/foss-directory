from pathlib import Path

from flask import render_template
from mistune import markdown
from pagic import Page


class FaqPage(Page):
    label = "FAQ"
    path = "/faq/"
    menu = "main"
    menu_order = 110

    def get(self):
        body_src = Path("content/faq.md").open().read()
        body = markdown(body_src)
        ctx = {
            "title": "A propos / FAQ",
            "body": body,
        }
        return render_template("pages/page.j2", **ctx)
