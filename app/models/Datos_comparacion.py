from app.database.sqlAlchemyORM import db
from datetime import datetime
import pandas as pd
import os


class Datos_comparacion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    credito = db.Column(db.String)
    fecha_ultima_modificacion = db.Column(db.DateTime)
    json = db.Column(db.String)

    def __init__(self, credito, json, file, add=True, flush=True, commit=True):
        datos_comparacion = Datos_comparacion.query.filter_by(credito=credito).first()
        if datos_comparacion is None:
            self.credito = credito
        else:
            self = datos_comparacion
        self.fecha_ultima_modificacion = datetime.now()
        if json is None:
            df = pd.read_excel(file.stream)
            self.json = df.to_json()
        else:
            self.json = json
        if add:
            db.session.add(self)
            if flush:
                db.session.flush()
                if commit:
                    db.session.commit()

    def dataframe(self):
        return pd.DataFrame.from_dict(self.json).reset_index(drop=True)

    def save_in_excel(self, path=None):
        if path is None:
            path = os.environ.get("PATH_DATOS_COMPARACION_TEMPS")
        df = self.dataframe()
        path_name = path+self.credito+'.xlsx'
        with pd.ExcelWriter(path_name) as writer:  
            df.to_excel(writer, sheet_name='datos_comparacion', index=False)

        return path_name

    def delete_temp(self, path=None):
        if path is None:
            path = os.environ.get("PATH_DATOS_COMPARACION_TEMPS")
        os.remove(path+self.credito+'.xlsx')

    def __repr__(self):
        return "<datos con id %r>" % self.id

#db.create_all()