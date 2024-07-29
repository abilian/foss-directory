# ruff: noqa: S105

import os

from dotenv import load_dotenv

load_dotenv()


class BaseConfig:
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    CACHE_TYPE = "simple"

    TEXTRAZOR_KEY = "410e7b2135f878f5a2814e09afe4bf070048d41f484910ecc680b7ac"

    SECRET_KEY = "hwoq123nzqqfrtdv809bndowke"
    BASIC_AUTH_USERNAME = "admin"
    BASIC_AUTH_PASSWORD = "yakafokon"


class DevConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = "postgresql:///annuaire-cnll"
    # SQLALCHEMY_ECHO = True

    DEBUG = True
    DEBUG_TB_ENABLED = True
    DEBUG_TB_INTERCEPT_REDIRECTS = False


class ProdConfig(BaseConfig):
    PG_USER = os.environ.get("PG_USER", "postgres")
    PG_PASSWORD = os.environ.get("PG_PASSWORD", "postgres")
    PG_HOST = os.environ.get("PG_HOST", "localhost")

    SQLALCHEMY_DATABASE_URI = (
        f"postgresql://{PG_USER}:{PG_PASSWORD}@{PG_HOST}/corpologia"
    )


ENVS = {
    "dev": DevConfig,
    "prod": ProdConfig,
}


def get_config():
    env = os.environ.get("FLASK_CONFIG", "dev")
    return ENVS[env]
