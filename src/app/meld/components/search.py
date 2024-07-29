# from flask_meld import Component
# from marshmallow import Schema, fields
# from sqlalchemy import func
#
# from app.extensions import db
# from app.models import Societe
#
#
# #
# # This shouldn't be needed...
# #
# class SocieteSchema(Schema):
#     nom = fields.Str()
#
#
# class Search(Component):
#     search = ""
#
#     @property
#     def societes(self):
#         search = self.search.lower()
#         societes = (
#             db.session.query(Societe)
#             .filter(func.lower(Societe.nom).contains(search))
#             .all()
#         )
#         return SocieteSchema().dump(societes, many=True)
