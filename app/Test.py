import pandas as pd
import numpy as np 
from app.Database import Database
from app.Log import Log
import json

class Test:
    def __init__(self, cod_demanda, num_credito, name_excel_results=None):
        self.cod_demanda = cod_demanda
        self.num_credito = num_credito
        if name_excel_results == None:
            self.name_excel_results = str(num_credito)+".xlsx"
        else:
            self.name_excel_results = name_excel_results
        self.db = Database(False)
        

    def make_test(self, with_num):
        if with_num:
            Log.i(__name__, f"Empezando test para el número de crédito: {self.num_credito}")
            df = self.db.leer_escritura(None, self.num_credito)
        else: 
            Log.i(__name__, f"Empezando test para el código de demanda: {self.cod_demanda}")
            df = self.db.leer_escritura(self.cod_demanda, None)

        id_cat_tipo_demanda = df.iloc[0]["id_cat_tipo_demanda"]
        json_datos_encontrados = json.loads(df.iloc[0]["json_datos_fundamentales"])
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
        
        results = pd.read_excel("app/results/"+str(self.name_excel_results))

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
            if str(row['valor_encontrado']) == str(row['valor_real']):
                if str(row['valor_real']).rstrip() != "":
                    tabla_entidades3.at[index,'texto_es_correcto'] = True
                    
        for index, row in tabla_entidades3.iterrows():
            if (row['pagina_encontrado'] == row['pagina_real']):
                tabla_entidades3.at[index,'pagina_es_correcta'] = True
            elif (row['pagina_encontrado'] == row['pagina_real']-1) and (row["texto_es_correcto"] == True):
                tabla_entidades3.at[index,'pagina_es_correcta'] = True

        correct_text = self.value_result_counts(tabla_entidades3, "texto_es_correcto")
        correct_pages = self.value_result_counts(tabla_entidades3, "pagina_es_correcta")
        
        result = {}
        result["num_credito"] = self.num_credito
        result["entidades_correctas"] = correct_text[0]
        result["entidades_incorrectas"] = correct_text[1]
        result["porcentaje_entidades_correctas"] = correct_text[0]/(correct_text[0]+correct_text[1])
        result["paginas_correctas"] = correct_pages[0]
        result["paginas_incorrectas"] = correct_pages[1]
        result["porcentaje_paginas_correctas"] = correct_pages[0]/(correct_pages[0]+correct_pages[1])
        result["entidades"] = self.put_bad_entities(tabla_entidades3, False)

        self.save_in_excel(tabla_entidades3, result)
        
        return result
    
    def get_tabla_entidades(self, id_cat_tipo_demanda, activo=True, modelo_ner="ner-escritura"):
        df1 = self.db.get_dato_fundamental(None, activo=activo)[["id_cat_dato_fundamental", "cod_dato_fundamental","entidad", "des_dato_fundamental","modelo_ner"]]
        df2 = self.db.get_demanda_dato_fundamental(id_cat_tipo_demanda)
        df3 = df2.merge(df1, on='id_cat_dato_fundamental')
        df3.sort_values(by=['des_dato_fundamental'], inplace=True)
        df4 = df3[df3["modelo_ner"]==modelo_ner].drop(columns=["modelo_ner"])
        
        return df4

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

    def put_bad_entities(self, df, send_empty_results):
        entities = { }
        df = df[df["texto_es_correcto"]==False]
        for index, row in df.iterrows():
            if not((send_empty_results==False) and (row['valor_real'] == "" or row['valor_real'] == "0")):
                entities[row["entidad"]] = { }
                entities[row["entidad"]]["valor_encontrado"] = row["valor_encontrado"]
                entities[row["entidad"]]["valor_real"] = row["valor_real"]
                entities[row["entidad"]]["pagina_encontrado"] = row["pagina_encontrado"]
                entities[row["entidad"]]["pagina_real"] = row["pagina_real"]
                entities[row["entidad"]]["texto_es_correcto"] = row["texto_es_correcto"]
                entities[row["entidad"]]["pagina_es_correcta"] = row["pagina_es_correcta"]
        
        return entities

    def save_in_excel(self, df, result):
        df2 = pd.DataFrame.from_dict(result, orient='index')
        with pd.ExcelWriter("app/results/reviewed/"+self.num_credito+'.xlsx') as writer:  
            df.to_excel(writer, sheet_name='table')
            df2.to_excel(writer, sheet_name='results')

