from sqlalchemy import create_engine 
import pandas as pd
import os
from dotenv import load_dotenv
from app.Log import Log

load_dotenv()


class DatabaseRobot:
    _port = os.environ.get("PORT_POSTGRESQL")
    _password = os.environ.get("PASSWORD_POSTGRESQL")
    _user_db = os.environ.get("USER_POSTGRESQL")
    _type_db = os.environ.get("TYPE_DB")
    endpoint_client = os.environ.get("ENDPOINT_CLIENT")
    endpoint_test = os.environ.get("ENDPOINT_TEST")
    database_robot = os.environ.get("DATABASE_ROBOT_LECTURA")
    def __init__(self, endpoint, database, port=_port, password=_password, user_db=_user_db, type_db=_type_db):
        Log.i(__name__, "Creating engine")
        self.engine = create_engine(f'{type_db}://{user_db}:{password}@{endpoint}:{port}/{database}')

    def query(self, command):
        return pd.read_sql(command, self.engine)

    def get_empty_entities(self):

        return self.query("""
            Select id_cat_dato_fundamental
            from grupo_entidades 
            where grupo_entidad='EMPTY'
            """
        )

    def get_cod_demanda(self, num_credito):
        df_db = self.query('''
            Select demanda.id_demanda, dato_relevante.num_credito, demanda.cod_demanda
            from demanda 
            inner join documento_procesado on demanda.id_demanda=documento_procesado.id_demanda
            inner join dato_relevante on documento_procesado.id_documento_procesado=(dato_relevante.id_documento_procesado)
            where dato_relevante.num_credito=\''''+str(num_credito)+'\'')

        try:
            return df_db.iloc[0]['cod_demanda']
        except IndexError:
            return None

    def leer_escritura(self, cod_demanda, num_credito):
        where = ""
        if cod_demanda is not None:
            where = "and demanda.cod_demanda="+str(cod_demanda)
        elif num_credito is not None:
            where = "and demanda.cod_demanda="+str(self.get_cod_demanda(num_credito))
        command = ('''
            Select demanda.id_demanda, id_cat_tipo_demanda, demanda.cod_demanda, documento_procesado.id_documento_procesado, documento_procesado.json_datos_fundamentales, documento_procesado.enlace_documento, pagina_procesada.numero_pagina, pagina_procesada.texto_procesado
            from demanda 
            inner join documento_procesado on demanda.id_demanda=documento_procesado.id_demanda
            inner join pagina_procesada on documento_procesado.id_documento_procesado=pagina_procesada.id_documento_procesado
            '''+ where
        )
        df_db = self.query(command)
        df_db['texto_procesado'] = df_db['texto_procesado'].apply(lambda x: str(x).replace("\n", " ").replace("\"","'"))
        df_db = df_db.sort_values(by=['cod_demanda','numero_pagina'])
        df_db.drop_duplicates(subset =["numero_pagina", "id_documento_procesado"], inplace = True)
        df_db.reset_index(drop=True, inplace=True)

        return df_db

    def get_dato_fundamental(self, cod_dato_fundamental, activo=None):
        if activo==None:
            if cod_dato_fundamental != None:
                df_db = self.query("""
                    Select *
                    from  cat_dato_fundamental 
                    where cod_dato_fundamental='"""+cod_dato_fundamental+"""'
                    """
                )
            else:
                df_db = self.query("""
                    Select *
                    from  cat_dato_fundamental
                    """
                )
        else:
            if cod_dato_fundamental != None:
                df_db = self.query("""
                    Select *
                    from  cat_dato_fundamental 
                    where activo=1 and cod_dato_fundamental='"""+cod_dato_fundamental+"""'
                    """
                )
            else:
                df_db = self.query("""
                    Select *
                    from  cat_dato_fundamental
                    where activo=1
                    """
                )

        return df_db

    def get_demanda_dato_fundamental(self, id_cat_tipo_demanda):
        df_db = self.query('''
            Select id_cat_dato_fundamental
            from tipo_demanda_dato_fundamental 
            where id_cat_tipo_demanda=\''''+str(id_cat_tipo_demanda)+'\''
        )

        return df_db    

    ## testing ## 

    def save_credito_testeado(self, num_credito):
        self.query(
            """
                INSERT INTO "credito-testeado"
                (credito, fecha)
                VALUES('"""+str(num_credito)+"""', now());
            """
        )

    def save_resultado(self, result):
        return self.query(
            """
                INSERT INTO resultado
                (   
                    entidades_correctas, entidades_incorrectas, 
                    num_credito, paginas_correctas, 
                    paginas_incorrectas, porcentaje_entidades_correctas, 
                    porcentaje_paginas_correctas
                )
                VALUES(
                    """+result["entidades_correctas"]+""", """+result["entidades_incorrectas"]+""", 
                    '"""+result["num_credito"]+"""', """+result["paginas_correctas"]+""",
                    """+result["paginas_incorrectas"]+""", """+result["porcentaje_entidades_correctas"]+""",
                    """+result["porcentaje_paginas_correctas"]+"""
                );
            """
        )
