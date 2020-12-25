from app.database.sqlAlchemyORM import db
from datetime import datetime

class Credito_testeado(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    credito = db.Column(db.String())
    fecha = db.Column(db.DateTime)

    def __init__(self, credito, add=True, flush=True):
        self.credito = credito
        self.fecha = datetime.now()
        if add:
            db.session.add(self)
            if flush:
                db.session.flush()

    def __repr__(self):
        return (f"<Credito {self.credito} con fecha {self.fecha}>")

#db.create_all()