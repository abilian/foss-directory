# from flask_sqlalchemy import SQLAlchemy
#
# from app.flask.sqla import get_multi, get_obj
# from app.models.auth import User
# from app.models.content.events import Event, PressEvent, PublicEvent
# from app.models.content.textual import Article
#
#
# def test_user(db: SQLAlchemy):
#     user = User(username="joe", email="joe@example.com")
#     db.session.add(user)
#     db.session.flush()
#
#     assert user.id is not None
#
#     user2 = get_obj(user.id, User)
#     assert user2 is user
#
#
# def test_article(db: SQLAlchemy):
#     owner = User(username="joe", email="joe@example.com")
#     article = Article(owner=owner)
#     db.session.add(article)
#     db.session.flush()
#
#
# def test_events(db: SQLAlchemy):
#     owner = User(username="joe", email="joe@example.com")
#     event1 = PressEvent(owner=owner)
#     db.session.add(event1)
#
#     event2 = PublicEvent(owner=owner)
#     db.session.add(event2)
#
#     db.session.flush()
#
#     events = set(get_multi(Event))
#     assert event1 in events
#     assert event2 in events
