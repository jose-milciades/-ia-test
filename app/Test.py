import pandas as pd
import numpy as np 
from app import database_test_robot
from app.models.Credito_testeado import Credito_testeado
from app.models.Resultado import Resultado
from app.models.Modelo_ner import Modelo_ner
from app.models.Entidad import Entidad
from app.models.Datos_comparacion import Datos_comparacion
from app.Log import Log
import json
import unidecode
from app.database.sqlAlchemyORM import db
from datetime import datetime
import os

class Test:
    credito_testeado: Credito_testeado
    resultado: Resultado
    modelos_ner: [ Modelo_ner ]
    entidades: [ Entidad ]
    def __init__(self, num_credito, send_with_correct_text, make_test=True, id_credito_testeado=None):
        self.send_with_correct_text = send_with_correct_text
        self.modelos_entidades = { }
        if id_credito_testeado is None:
            self.credito_testeado = Credito_testeado(num_credito)
            self.db = database_test_robot
            self.modelos_ner = [ ]
            self.entidades = [ ]
            if make_test:
                self.make_test()
        else:
            self.read_test(id_credito_testeado)

    def read_test(self, id_credito_testeado):
        self.credito_testeado = Credito_testeado.query.filter_by(id=id_credito_testeado).first()
        self.resultado = Resultado.query.filter_by(id_credito_testeado=id_credito_testeado).first()
        self.modelos_ner = Modelo_ner.query.filter_by(id_resultado=self.resultado.id).all()
        self.entidades = [ ]
        modelos_ner_id = [ ]
        for modelo_ner in self.modelos_ner:
            modelos_ner_id.append(modelo_ner.id)
        self.entidades = Entidad.query.filter(Entidad.id_modelo_ner.in_(modelos_ner_id)).all()
        self.modelos_entidades["entidades"] = self.put_entities(None, self.send_with_correct_text, False)

    def make_test(self):
        Log.i(__name__, f"Empezando test para el número de crédito: {self.credito_testeado.credito}")
        df = self.db.leer_escritura(None, self.credito_testeado.credito)

        id_cat_tipo_demanda = df.iloc[0]["id_cat_tipo_demanda"]
        json_datos_encontrados = {"datoFundamental": []}
        for json_ in list(df["json_datos_fundamentales"].unique()):
            aux_json = json.loads(json_)
            if len(aux_json["datoFundamental"])>0:
                for dato in aux_json["datoFundamental"]:
                    json_datos_encontrados["datoFundamental"].append(dato)
        #json_datos_encontrados = json.loads(df.iloc[0]["json_datos_fundamentales"])
        tabla_entidades = self.get_tabla_entidades(id_cat_tipo_demanda)
        tabla_entidades["valor_encontrado"] = tabla_entidades["cod_dato_fundamental"].apply(lambda x: self.get_valor_encontrado(json_datos_encontrados, x))
        tabla_entidades["pagina_encontrado"] = tabla_entidades["cod_dato_fundamental"].apply(lambda x: self.get_pagina_valor_encontrado(json_datos_encontrados, x))
        tabla_entidades["pagina_encontrado"] = tabla_entidades["pagina_encontrado"].apply(lambda x: self.deleteNan(x, False))
        tabla_entidades2 = tabla_entidades.copy()
        df_empty = self.db.get_empty_entities()
        tabla_entidades2 = tabla_entidades2[~tabla_entidades2.id_cat_dato_fundamental.isin(list(df_empty["id_cat_dato_fundamental"]))]
        tabla_entidades2 = tabla_entidades2[~tabla_entidades2.entidad.isin(["PORCENTAJE_REA", "COLINDANCIAS_10", "COLINDANCIAS_11", "COLINDANCIAS_12", "COLINDANCIAS_5", "COLINDANCIAS_6", "COLINDANCIAS_7", "COLINDANCIAS_8", "COLINDANCIAS_9"])]
        tabla_entidades_vacias = self.get_entidades_vacias(tabla_entidades2)

        Log.i(__name__, f"Cantidad de entidades a encontrar: {len(tabla_entidades2)}")
        Log.i(__name__, f"Cantidad de entidades vacías: {len(tabla_entidades_vacias)}")
        Log.i(__name__, f"Porcentaje de entidades encontradas: {(len(tabla_entidades2)-len(tabla_entidades_vacias))/len(tabla_entidades2)}")

        datos_comparacion = Datos_comparacion.query.filter_by(credito=self.credito_testeado.credito).first()
        
        results = datos_comparacion.dataframe()

        tabla_entidades3 = tabla_entidades2.copy()
        tabla_entidades3["valor_real"] = ""
        tabla_entidades3["pagina_real"] = ""
        tabla_entidades3.reset_index(inplace=True,drop=True)

        for index, row in tabla_entidades3.iterrows():
            x = row['des_dato_fundamental']
            value = str(results[results["ENTIDAD"] == x]["DATO REAL"].iloc[0]) if len(results[results["ENTIDAD"] == x])>0 else ""
            tabla_entidades3.at[index,'valor_real'] = value.upper()

        for index, row in tabla_entidades3.iterrows():
            x = row['des_dato_fundamental']
            value = str(results[results["ENTIDAD"] == x]["PAGINA"].iloc[0]) if len(results[results["ENTIDAD"] == x])>0 else ""
            try:
                tabla_entidades3.at[index,'pagina_real'] = int(float(value))
            except:
                tabla_entidades3.at[index,'pagina_real'] = -1

        tabla_entidades3["texto_es_correcto"] = False
        tabla_entidades3["pagina_es_correcta"] = False

        for index, row in tabla_entidades3.iterrows():
            if unidecode.unidecode(str(row['valor_encontrado'])) == unidecode.unidecode(str(row['valor_real'])):
                if str(row['valor_real']).rstrip() != "":
                    tabla_entidades3.at[index,'texto_es_correcto'] = True
                    
        for index, row in tabla_entidades3.iterrows():
            if (row['pagina_encontrado'] == row['pagina_real']):
                tabla_entidades3.at[index,'pagina_es_correcta'] = True
            elif (row['pagina_encontrado'] == row['pagina_real']-1) and (row["texto_es_correcto"] == True):
                tabla_entidades3.at[index,'pagina_es_correcta'] = True

        correct_text = self.value_result_counts(tabla_entidades3, "texto_es_correcto")
        correct_pages = self.value_result_counts(tabla_entidades3, "pagina_es_correcta")

        self.resultado = Resultado(entidades_correctas=correct_text[0], entidades_incorrectas=correct_text[1],
                                paginas_correctas=correct_pages[0], paginas_incorrectas=correct_pages[1], 
                                porcentaje_entidades_correctas=correct_text[0]/(correct_text[0]+correct_text[1]), 
                                porcentaje_paginas_correctas=correct_pages[0]/(correct_pages[0]+correct_pages[1]), 
                                id_credito_testeado=self.credito_testeado.id)
        self.modelos_entidades["entidades"] = self.put_entities(tabla_entidades3, self.send_with_correct_text, False)
        #self.save_in_excel(tabla_entidades3, json.loads(self.__repr__()))
        self.save_all_models()
    
    def get_tabla_entidades(self, id_cat_tipo_demanda, activo=True):
        df1 = self.db.get_dato_fundamental(None, activo=activo)[["id_cat_dato_fundamental", "cod_dato_fundamental","entidad", "des_dato_fundamental","modelo_ner"]]
        df2 = self.db.get_demanda_dato_fundamental(id_cat_tipo_demanda)
        df3 = df2.merge(df1, on='id_cat_dato_fundamental')
        df3.sort_values(by=['des_dato_fundamental'], inplace=True)
        
        return df3

    def get_valor_encontrado(self, json_datos_encontrados, cod_dato_fundamental):
        for dato_fundamental in json_datos_encontrados["datoFundamental"]:
            if dato_fundamental["codDatoFundamental"] == cod_dato_fundamental:
                return dato_fundamental["valor"]
        
    def get_pagina_valor_encontrado(self, json_datos_encontrados, cod_dato_fundamental):
        for dato_fundamental in json_datos_encontrados["datoFundamental"]:
            if dato_fundamental["codDatoFundamental"] == cod_dato_fundamental:
                return dato_fundamental["numPaginaDocumento"]

    def deleteNan(self, x, returnString):
        try:
            int(x)
            if returnString:
                return str(x)
            else:
                return int(x)
        except:
            if returnString:
                return ""
            else:
                return 0

    def get_entidades_vacias(self, df, columna="valor_encontrado", espacio=True, vacia=True):
        df_ = pd.DataFrame()
        if espacio:
            df_ = df_.append(df[df[columna] == " "])
        if vacia:
            df_ = df_.append(df[df[columna] == ""])
        return df_

    def value_result_counts(self, df, column):
        Log.i(__name__, "Value counts")
        Log.i(__name__, df[column].value_counts())
        true = 0 
        false = 0
        for index, row in df.iterrows():
            if (row['valor_real'] != "" and row['valor_real'] != "0"):
                if row[column]:
                    true = true + 1
                else:
                    false = false + 1
        Log.i(__name__, "Eliminando entidades no encontradas en el excel de resultados:")
        Log.i(__name__, f"True: {true}")
        Log.i(__name__, f"False: {false}")
        return true, false

    def put_entities(self, df, send_with_correct_text, send_empty_results):
        entities = { }
        
        if df is not None:
            for model in list(df["modelo_ner"].unique()):
                correct_text = self.value_result_counts(df[df["modelo_ner"]==model], "texto_es_correcto")
                correct_pages = self.value_result_counts(df[df["modelo_ner"]==model], "pagina_es_correcta")
                try:
                    porcentaje_entidades_correctas = correct_text[0]/(correct_text[0]+correct_text[1])
                except ZeroDivisionError:
                    porcentaje_entidades_correctas = 1
                try:
                    porcentaje_paginas_correctas = correct_pages[0]/(correct_pages[0]+correct_pages[1])
                except ZeroDivisionError:
                    porcentaje_paginas_correctas = 1

                modelo_ner = Modelo_ner(modelo_ner=model, entidades_correctas=correct_text[0], entidades_incorrectas=correct_text[1],
                                        paginas_correctas=correct_text[0], paginas_incorrectas=correct_text[1], 
                                        porcentaje_entidades_correctas=porcentaje_entidades_correctas, 
                                        porcentaje_paginas_correctas=porcentaje_paginas_correctas, id_resultado=self.resultado.id)
                self.modelos_ner.append(modelo_ner)
        
            if len(self.entidades) == 0:
                for index, row in df.iterrows():
                    if not((send_empty_results==False) and (row['valor_real'] == "" or row['valor_real'] == "0")):
                        model = None
                        for modelo in self.modelos_ner:
                            if modelo.modelo_ner == row["modelo_ner"]:
                                model = modelo
                                break
                        self.entidades.append(
                            Entidad(entidad=row["entidad"], pagina_encontrado=row["pagina_encontrado"], 
                                    pagina_es_correcta=row["pagina_es_correcta"], pagina_real=row["pagina_real"], 
                                    texto_es_correcto=row["texto_es_correcto"], valor_encontrado=row["valor_encontrado"],
                                    valor_real=row["valor_real"], id_modelo_ner=model.id)
                        )
        for modelo in self.modelos_ner:
            modelo_dict = json.loads(str(modelo))
            for entidad in self.entidades:
                if entidad.id_modelo_ner == modelo.id:
                    if (not send_with_correct_text and not entidad.texto_es_correcto) or (send_with_correct_text):
                        entidad_dict = json.loads(str(entidad))
                        modelo_dict[modelo.modelo_ner][entidad.entidad] = entidad_dict
            entities = {**entities, **modelo_dict}
        return entities

    def save_in_excel(self, df, result, path=None):
        if result is None:
            result = json.loads(self.__repr__())
        if path is None:
            path = os.environ.get("PATH_RESULTS_TEMPS")
        df2 = pd.DataFrame.from_dict(result, orient='index')
        path_name = path+self.credito_testeado.credito+'_resultado.xlsx'
        with pd.ExcelWriter(path_name) as writer:  
            df2.to_excel(writer, sheet_name='results')
            if df is not None:
                df.to_excel(writer, sheet_name='table')

        return path_name

    def delete_temp(self, path=None):
        if path is None:
            path = os.environ.get("PATH_RESULTS_TEMPS")
        os.remove(path+self.credito_testeado.credito+'_resultado.xlsx')

    def save_all_models(self):
        db.session.commit()
        Log.i(__name__, "Todos los modelos han sido almacenados")

    def __repr__(self):
        resultado = json.loads(str(self.resultado))
        result = {**resultado, **self.modelos_entidades}
        return json.dumps(result)

