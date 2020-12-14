from sqlalchemy import create_engine
import pandas as pd

class Database:
    def __init__(self, endpoint_client):
        if endpoint_client:
            self.engine = create_engine('postgresql://postgres:securep@sshere@192.168.0.22:5432/robotLectura')
        else: 
            self.engine = create_engine('postgresql://postgres:securep@sshere@192.168.0.11:5432/robotLectura')

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
