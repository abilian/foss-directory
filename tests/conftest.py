"""Configuration and injectable fixtures for Pytest."""
from __future__ import annotations

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from pytest import fixture
from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db as _db
from app.main import create_app


class TestConfig:
    TESTING = True
    CSRF_ENABLED = False
    MAIL_SENDER = "test@example.com"
    MAIL_SUPPRESS_SEND = True
    SECRET_KEY = "changeme"
    SERVER_NAME = "localhost.localdomain"
    # SQLALCHEMY_DATABASE_URI = "sqlite://"
    SQLALCHEMY_DATABASE_URI = "postgresql://localhost/annuaire_test"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CACHE_NO_NULL_WARNING = True


@fixture(scope="session")
def app() -> Flask:
    """We usually only create an app once per session."""

    return create_app(TestConfig)


@fixture
def app_context(app: Flask):
    with app.app_context() as ctx:
        yield ctx


@fixture
def request_context(app: Flask):
    with app.test_request_context() as ctx:
        yield ctx


@fixture
def db(app: Flask) -> SQLAlchemy:
    """Return a fresh db for each test."""

    with app.app_context():
        cleanup_db(_db)
        _db.create_all()

        yield _db

        _db.session.remove()
        cleanup_db(_db)

        _db.session.flush()


@fixture
def db_session(db: SQLAlchemy):
    """Kept for historical reasons."""

    return db.session


@fixture
def client(app, db):
    """Return a Web client, used for testing, bound to a DB session."""
    return app.test_client()


#
# Cleanup utilities
#
def cleanup_db(db):
    """Drop all the tables, in a way that doesn't raise integrity errors."""

    for table in reversed(db.metadata.sorted_tables):
        try:
            db.session.execute(table.delete())
        except SQLAlchemyError:
            print(f"Failed to delete table {table}")
            pass
