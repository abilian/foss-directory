from __future__ import annotations

from flask import jsonify

from . import route


@route("/api/clusters/")
def clusters():
    clusters_ = [
        "Adhérent direct",
        "Alliance Libre",
        "CapLibre",
        "HOS",
        "Libertis",
        "NAOS",
        "Ploss-ra",
        "SoLibre",
        "Telecom Valley",
    ]
    return jsonify(clusters_)


# @route("/api/solutions/")
# def solutions():
#     solutions = db.session.query(Solution).order_by(Solution.id).all()
#     dto = [solution.id for solution in solutions]
#     return jsonify(solutions=dto)
