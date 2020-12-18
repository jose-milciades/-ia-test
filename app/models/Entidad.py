from app.database.sqlAlchemyORM import db
import json

class Entidad(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    entidad = db.Column(db.String)
    pagina_encontrado = db.Column(db.Integer)
    pagina_es_correcta = db.Column(db.Boolean)
    pagina_real = db.Column(db.Integer)
    texto_es_correcto = db.Column(db.Boolean)
    valor_encontrado = db.Column(db.String)
    valor_real = db.Column(db.String)
    id_modelo_ner = db.Column(db.Integer, db.ForeignKey('modelo_ner.id'))

    def __init__(self, entidad, pagina_encontrado, pagina_es_correcta, pagina_real, texto_es_correcto, 
                    valor_encontrado, valor_real, id_modelo_ner, add=True, flush=True):
        self.entidad = entidad
        self.pagina_encontrado = pagina_encontrado
        self.pagina_es_correcta = pagina_es_correcta
        self.pagina_real = pagina_real
        self.texto_es_correcto = texto_es_correcto
        self.valor_encontrado = valor_encontrado
        self.valor_real = valor_real
        self.id_modelo_ner = id_modelo_ner
        if add:
            db.session.add(self)
            if flush:
                db.session.flush()

    def __repr__(self):
        result = {}
        result["pagina_encontrado"] = self.pagina_encontrado
        result["pagina_es_correcta"] = self.pagina_es_correcta
        result["pagina_real"] = self.pagina_real
        result["texto_es_correcto"] = self.texto_es_correcto
        result["valor_encontrado"] = self.valor_encontrado
        result["valor_real"] = self.valor_real
        return json.dumps(result)

#db.create_all()