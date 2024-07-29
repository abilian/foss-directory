import sys

import sentry_sdk
from flask import Flask
from flask_migrate import Migrate
from loguru import logger
from pagic.macros import register_macros
from pagic.pagic import Pagic
from sentry_sdk.integrations.flask import FlaskIntegration

from . import cli, debugging
from .admin.views import register_admin_views
from .blueprints.public import blueprint as public_blueprint
from .config import get_config
from .extensions import admin, basic_auth, cache, cors, db, tailwind, toolbar
from .lib.scanner import scan_modules
from .services.register import register_services

PAGES = "app.pages"
MACROS = "app.macros"
BLUEPRINTS = "app.blueprints"

logger.remove(0)
logger.add(
    sys.stderr,
    colorize=True,
    format="{time:MMMM D, YYYY > HH:mm:ss} | {level} | {message} | {extra}",
)
debugging.install()


def create_app(config=None):
    app = Flask(__name__)

    set_config(app, config)

    register_services(app)

    pagic = Pagic(app)
    pagic.scan_pages(PAGES)

    register_extensions(app)

    scan_modules(BLUEPRINTS)
    register_blueprints(app)

    register_cli(app)
    register_macros(app, MACROS)

    # app.before_request(inject_nav)

    return app


def set_config(app, config: dict | None):
    if config:
        app.config.from_object(config)
    else:
        app.config.from_object(get_config())
        app.config.from_prefixed_env()


def register_extensions(app):
    db.init_app(app)
    Migrate(app, db)
    cache.init_app(app)
    if toolbar:
        toolbar.init_app(app)
    cors.init_app(app)
    admin.init_app(app)
    # assert admin_views
    tailwind.init_app(app)
    # meld.init_app(app)
    basic_auth.init_app(app)

    register_admin_views(admin)

    if app.config.get("SENTRY_DSN"):
        sentry_sdk.init(
            dsn=app.config["SENTRY_DSN"],
            integrations=[FlaskIntegration()],
            traces_sample_rate=0.25,
            send_default_pii=True,
        )


def register_cli(app):
    cli.register_commands(app)


def register_blueprints(app):
    app.register_blueprint(public_blueprint)
