# Add model views
from flask_admin.contrib.sqla import ModelView
from flask_admin.menu import MenuLink
from wtforms import TextAreaField

from app.extensions import basic_auth, db
from app.models import Societe, Solution


class MyModelView(ModelView):
    # Sensible defaults
    can_view_details = True  # show a modal dialog with records details
    # can_create = False
    can_delete = False

    def is_accessible(self):
        return basic_auth.authenticate()

    def inaccessible_callback(self, name, **kwargs):
        return basic_auth.challenge()

    def __init__(self, *args, **kw):
        if hasattr(self, "category"):
            kw["category"] = self.category
        if hasattr(self, "name"):
            kw["name"] = self.name

        super().__init__(self.model, db.session, *args, **kw)


class SocieteAdmin(MyModelView):
    model = Societe

    column_list = [
        "nom",
        "active",
        "metier",
        "clusters",
    ]
    column_searchable_list = [
        "nom",
    ]

    form_columns = [
        "siren",
        "nom",
        "site_web",
        "metier",
        "solutions",
        "active",
        "clusters",
        "description",
    ]

    form_overrides = {"description": TextAreaField}


class SolutionAdmin(MyModelView):
    model = Solution
    can_edit = True
    can_delete = True

    column_list = [
        "name",
        "home_url",
    ]
    column_searchable_list = [
        "name",
    ]
    form_columns = [
        "name",
        "slug",
        "home_url",
        "description",
        "societes",
    ]

    form_overrides = {"description": TextAreaField}


def register_admin_views(admin):
    admin.add_view(SocieteAdmin())
    admin.add_view(SolutionAdmin())
    admin.add_link(MenuLink(name="Public site", url="/"))
