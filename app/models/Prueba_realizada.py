from app.database.sqlAlchemyORM import db
from datetime import datetime


class Prueba_realizada(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.DateTime)
    json_resultado = db.Column(db.String)

    def __init__(self, json, add=True, flush=True):
        self.json_resultado = json
        self.fecha = datetime.now()
        if add:
            db.session.add(self)
            if flush:
                db.session.flush()

    def __repr__(self):
        return "<Prueba_realizada %r>" % self.id

#db.create_all()