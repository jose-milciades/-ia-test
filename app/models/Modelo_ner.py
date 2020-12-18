from app.database.sqlAlchemyORM import db
import json

class Modelo_ner(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    modelo_ner = db.Column(db.String)
    entidades_correctas = db.Column(db.Integer)
    entidades_incorrectas = db.Column(db.Integer)
    paginas_correctas = db.Column(db.Integer)
    paginas_incorrectas = db.Column(db.Integer)
    porcentaje_entidades_correctas = db.Column(db.Float)
    porcentaje_paginas_correctas = db.Column(db.Float)
    id_resultado = db.Column(db.Integer, db.ForeignKey('resultado.id'))

    def __init__(self, modelo_ner, entidades_correctas, entidades_incorrectas, paginas_correctas, paginas_incorrectas, 
                    porcentaje_entidades_correctas, porcentaje_paginas_correctas, id_resultado, add=True, flush=True):
        self.modelo_ner = modelo_ner
        self.entidades_correctas = entidades_correctas
        self.entidades_incorrectas = entidades_incorrectas
        self.paginas_correctas = paginas_correctas
        self.paginas_incorrectas = paginas_incorrectas
        self.porcentaje_entidades_correctas = porcentaje_entidades_correctas
        self.porcentaje_paginas_correctas = porcentaje_paginas_correctas
        self.id_resultado = id_resultado
        if add:
            db.session.add(self)
            if flush:
                db.session.flush()

    def __repr__(self):
        result = {}
        result[self.modelo_ner] = { }
        result[self.modelo_ner]["entidades_correctas"] = self.entidades_correctas
        result[self.modelo_ner]["entidades_incorrectas"] = self.entidades_incorrectas
        result[self.modelo_ner]["porcentaje_entidades_correctas"] = self.porcentaje_entidades_correctas
        result[self.modelo_ner]["paginas_correctas"] = self.paginas_correctas
        result[self.modelo_ner]["paginas_incorrectas"] = self.paginas_incorrectas
        result[self.modelo_ner]["porcentaje_paginas_correctas"] = self.porcentaje_paginas_correctas
        return json.dumps(result)

#db.create_all()