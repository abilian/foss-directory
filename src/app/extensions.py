from flask_admin import Admin
from flask_basicauth import BasicAuth
from flask_caching import Cache
from flask_cors import CORS

# from flask_meld import Meld
from flask_sqlalchemy import SQLAlchemy
from flask_tailwind import Tailwind

from app.models.base import Base

db = SQLAlchemy(model_class=Base)
cache = Cache()

cors = CORS()
admin = Admin(template_mode="bootstrap4")
tailwind = Tailwind()
basic_auth = BasicAuth()

try:
    from flask_debugtoolbar import DebugToolbarExtension

    toolbar = DebugToolbarExtension()
except ImportError:
    toolbar = None

# meld = Meld()
