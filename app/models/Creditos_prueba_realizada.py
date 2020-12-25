from app.database.sqlAlchemyORM import db

class Creditos_prueba_realizada(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_prueba_realizada = db.Column(db.Integer, db.ForeignKey('prueba_realizada.id'))
    id_credito_testeado = db.Column(db.Integer, db.ForeignKey('credito_testeado.id'))

    def __init__(self, id_prueba_realizada, id_credito_testeado, add=True, flush=True):
        self.id_prueba_realizada = id_prueba_realizada
        self.id_credito_testeado = id_credito_testeado
        if add:
            db.session.add(self)
            if flush:
                db.session.flush()

    def __repr__(self):
        return "<Creditos_prueba_realizada id %rr>" % self.id

#db.create_all()