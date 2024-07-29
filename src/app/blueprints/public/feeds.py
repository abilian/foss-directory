import sqlalchemy as sa
from flask import Response, render_template
from pagic import url_for

from app.extensions import db
from app.models import Societe

from . import blueprint


@blueprint.route("/sitemap.xml")
def sitemap():
    urls = []

    stmt = sa.select(Societe).where(Societe.active == True)
    result = db.session.execute(stmt)
    societes: list[Societe] = list(result.scalars())

    for societe in societes:
        # TODO: change 'private' to 'public'
        url = {
            "loc": url_for(societe, _external=True),
            # "lastmod": societe.modified_at.strftime("%Y-%m-%d"),
            "changefreq": "daily",
        }
        urls.append(url)

    body = render_template("sitemap.j2", urls=urls)
    return Response(body, mimetype="text/xml")
