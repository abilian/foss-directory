import svcs
from svcs.flask import (
    close_registry,
    get,
    get_pings,
    init_app,
    overwrite_factory,
    overwrite_value,
    register_factory,
    register_value,
    svcs_from,
)

__all__ = [
    "close_registry",
    "get_pings",
    "get",
    "init_app",
    "overwrite_factory",
    "overwrite_value",
    "register_factory",
    "register_services",
    "register_value",
    "svcs_from",
]

from .config import Config
from .screenshots import ScreenshotService

SERVICES: list[type] = [
    ScreenshotService,
    Config,
]


def register_services(app):
    svcs.flask.init_app(app)
    for service in SERVICES:
        register_factory(app, service, service)
