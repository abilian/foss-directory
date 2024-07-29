from werkzeug.routing import Rule


def test_create_app(app):
    assert app

    rules: list[Rule] = list(app.url_map.iter_rules())
    rules2 = []
    for rule in rules:
        if rule.rule.startswith("/_"):
            continue
        if rule.rule.startswith("/admin/"):
            continue
        if rule.rule.startswith("/static/"):
            continue
        rules2.append(rule)

    assert len(rules2) > 0
