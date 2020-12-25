from app.database.sqlAlchemyORM import db
import json

class Resultado(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    entidades_correctas = db.Column(db.Integer)
    entidades_incorrectas = db.Column(db.Integer)
    paginas_correctas = db.Column(db.Integer)
    paginas_incorrectas = db.Column(db.Integer)
    porcentaje_entidades_correctas = db.Column(db.Float)
    porcentaje_paginas_correctas = db.Column(db.Float)
    id_credito_testeado = db.Column(db.Integer, db.ForeignKey('credito_testeado.id'))

    def __init__(self, entidades_correctas, entidades_incorrectas, paginas_correctas, paginas_incorrectas, 
                    porcentaje_entidades_correctas, porcentaje_paginas_correctas, id_credito_testeado, add=True, flush=True):
        self.entidades_correctas = entidades_correctas
        self.entidades_incorrectas = entidades_incorrectas
        self.paginas_correctas = paginas_correctas
        self.paginas_incorrectas = paginas_incorrectas
        self.porcentaje_entidades_correctas = porcentaje_entidades_correctas
        self.porcentaje_paginas_correctas = porcentaje_paginas_correctas
        self.id_credito_testeado = id_credito_testeado
        if add:
            db.session.add(self)
            if flush:
                db.session.flush()

    def __repr__(self):
        result = {}
        result["id_credito_testeado"] = self.id_credito_testeado
        result["entidades_correctas"] = self.entidades_correctas
        result["entidades_incorrectas"] = self.entidades_incorrectas
        result["porcentaje_entidades_correctas"] = self.porcentaje_entidades_correctas
        result["paginas_correctas"] = self.paginas_correctas
        result["paginas_incorrectas"] = self.paginas_incorrectas
        result["porcentaje_paginas_correctas"] = self.porcentaje_paginas_correctas
        return json.dumps(result)

#db.create_all()