# from devtools import debug
# from flask import g, request, url_for
#
# NAV = [
#     (".home", "Annuaire"),
#     (".home", "Carte"),
#     (".clusters", "Clusters"),
#     (".regions", "Régions"),
#     (".villes", "Villes"),
#     (".solutions", "Solutions"),
#     (".faq", "FAQ"),
# ]
#
#
# def inject_nav():
#     endpoint = request.endpoint
#     if not endpoint:
#         return
#     blueprint = endpoint.split(".")[0]
#     if blueprint != "public":
#         return
#
#     g.nav = make_nav()
#
#
# def make_nav():
#     nav = []
#     active_entries = []
#     for endpoint, label in NAV:
#         debug(endpoint, label)
#         url = url_for(endpoint)
#         if request.path.startswith(url):
#             active_entries.append([url, endpoint])
#         nav.append({"label": label, "url": url, "endpoint": endpoint, "active": False})
#
#     active_entries.sort(key=lambda x: -len(x[0]))
#     if active_entries:
#         active_endpoint = active_entries[0][1]
#         for entry in nav:
#             if entry["endpoint"] == active_endpoint:
#                 entry["active"] = True
#
#     return nav
