from flask_sqlalchemy import SQLAlchemy
from pagic import url_for
from pytest import mark
from werkzeug.routing import Rule


def test_404(client):
    res = client.get("/asdasd")
    assert res.status_code == 404


def test_home(db: SQLAlchemy, client):
    # stuff = _create_stuff(db)
    res = client.get(url_for("home"))
    assert res.status_code == 200


def test_solutions(db: SQLAlchemy, client):
    # stuff = _create_stuff(db)
    res = client.get(url_for("solutions"))
    assert res.status_code == 200


def test_clusters(db: SQLAlchemy, client):
    # stuff = _create_stuff(db)
    res = client.get(url_for("clusters"))
    assert res.status_code == 200


def test_villes(db: SQLAlchemy, client):
    # stuff = _create_stuff(db)
    res = client.get(url_for("villes"))
    assert res.status_code == 200


def test_regions(db: SQLAlchemy, client):
    # stuff = _create_stuff(db)
    res = client.get(url_for("regions"))
    assert res.status_code == 200


def test_all_unparameterized_endpoints(app, db: SQLAlchemy, client):
    # _create_stuff(db)

    bad_prefixes = [
        "/_",
        "/admin/",
        "/static/",
    ]

    rules: list[Rule] = list(app.url_map.iter_rules())
    for rule in rules:
        if any(rule.rule.startswith(p) for p in bad_prefixes):
            continue

        if "<" in rule.rule:
            continue

        res = client.get(rule.rule)
        assert res.status_code in (302, 200), f"Request failed on {rule.rule}"


@mark.skip
def test_wire(db: SQLAlchemy, client):
    stuff = _create_stuff(db)

    res = client.get(url_for("wire.wire"))
    # FIXME
    # assert res.status_code == 302
    assert res.status_code in [302, 200]

    res = client.get(url_for("wire.wire", current_tab="wires"))
    assert res.status_code == 200

    res = client.get(url_for("wire.article", id=stuff["article"].id))
    assert res.status_code == 200


@mark.skip
def test_members(db: SQLAlchemy, client):
    ctx = _create_stuff(db)
    res = client.get(url_for("swork.members"))
    assert res.status_code == 200

    res = client.get(url_for("swork.profile"))
    assert res.status_code == 302

    res = client.get(url_for("swork.member", id=ctx["user"].id))
    assert res.status_code == 200


@mark.skip
def test_events(db: SQLAlchemy, client):
    _create_stuff(db)
    res = client.get(url_for("events.events"))
    assert res.status_code in {200, 302}

    res = client.get(url_for("events.events", current_tab="all"))
    assert res.status_code == 200


# def test_search(db: SQLAlchemy, client):
#     _create_stuff(db)
#     res = client.get(url_for("private.search"))
#     assert res.status_code == 200


@mark.skip
def test_wip(db: SQLAlchemy, client):
    _create_stuff(db)
    res = client.get(url_for("wip.wip"))
    assert res.status_code == 302

    res = client.get(url_for("wip.dashboard"))
    assert res.status_code == 200


def _create_stuff(db: SQLAlchemy):
    pass
    # owner = User(username="joe", email="joe@example.com")
    # db.session.add(owner)
    # article = Article(owner=owner)
    # db.session.add(article)
    # db.session.flush()
    #
    # return {
    #     "user": owner,
    #     "article": article,
    # }
