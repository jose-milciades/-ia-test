from app.Test import Test
from app.models.Prueba_realizada import Prueba_realizada
from app.models.Creditos_prueba_realizada import Creditos_prueba_realizada
from app.models.Credito_testeado import Credito_testeado
import json
from app.Log import Log
from app.database.sqlAlchemyORM import db
from app import views

class Test_resume:
    tests: { Test }
    id_prueba_realizada: int
    resume = { }
    
    def __init__(self, tests, make_resume=True, save_resume=True, id_prueba_realizada=None):
        if tests is not None:
            self.tests = tests
            if make_resume:
                self.resumen()
            if save_resume:
                self.save()
        elif id_prueba_realizada is not None:
            self.id_prueba_realizada = id_prueba_realizada
            prueba_realizada = Prueba_realizada.query.filter_by(id=id_prueba_realizada).first()
            creditos_prueba_realizada = Creditos_prueba_realizada.query.filter_by(id_prueba_realizada=id_prueba_realizada).all()
            creditos = [ ]
            self.tests = { }
            for credito_prueba_realizada in creditos_prueba_realizada:
                creditos.append(Credito_testeado.query.filter_by(id=credito_prueba_realizada.id_credito_testeado).first())
            t = None
            for credito in creditos:
                t = Test(None, True, id_credito_testeado=credito.id)
                self.tests[t.credito_testeado.credito] = (json.loads(t.__repr__()))
            if make_resume:
                self.resumen()

    def resumen(self):
        total_correct_entities = 0
        total_incorrect_entities = 0
        total_correct_pages = 0
        total_incorrect_pages = 0
        percent_correct_entities = 0
        percent_correct_pages = 0
        entities = { } 
        credits_ = []
        for key, value in self.tests.items():
            credits_.append(key)
            total_correct_entities = total_correct_entities+value["entidades_correctas"]
            total_incorrect_entities = total_incorrect_entities+value["entidades_incorrectas"]
            total_correct_pages = total_correct_pages+value["paginas_correctas"]
            total_incorrect_pages = total_incorrect_pages+value["paginas_incorrectas"]
            for model_ner, values_model in value["entidades"].items():
                if not model_ner in entities:
                    entities[model_ner] = { }
                del value["entidades"][model_ner]["entidades_correctas"]
                del value["entidades"][model_ner]["entidades_incorrectas"]
                del value["entidades"][model_ner]["paginas_correctas"]
                del value["entidades"][model_ner]["paginas_incorrectas"]
                del value["entidades"][model_ner]["porcentaje_entidades_correctas"]
                del value["entidades"][model_ner]["porcentaje_paginas_correctas"]
                for key_e, value_e in value["entidades"][model_ner].items():
                    if not key_e in entities[model_ner]:
                        entities[model_ner][key_e] = { }
                    if value_e["texto_es_correcto"]:
                        if not "entidades_correctas" in entities[model_ner][key_e]:
                            entities[model_ner][key_e]["entidades_correctas"] = 1
                        else:
                            entities[model_ner][key_e]["entidades_correctas"] = entities[model_ner][key_e]["entidades_correctas"] + 1
                    else:
                        if not "entidades_incorrectas" in entities[model_ner][key_e]:
                            entities[model_ner][key_e]["entidades_incorrectas"] = 1
                        else:
                            entities[model_ner][key_e]["entidades_incorrectas"] = entities[model_ner][key_e]["entidades_incorrectas"] + 1
                    if not "entidades_correctas" in entities[model_ner][key_e]:
                        entities[model_ner][key_e]["porcentaje_entidades_correctas"] = 0
                    elif not "entidades_incorrectas" in entities[model_ner][key_e]:
                        entities[model_ner][key_e]["porcentaje_entidades_correctas"] = 1
                    else:
                        entities[model_ner][key_e]["porcentaje_entidades_correctas"] = (
                            entities[model_ner][key_e]["entidades_correctas"]/
                            (entities[model_ner][key_e]["entidades_correctas"]+entities[model_ner][key_e]["entidades_incorrectas"])
                        )
                    #pages
                    if value_e["pagina_es_correcta"]:
                        if not "paginas_correctas" in entities[model_ner][key_e]:
                            entities[model_ner][key_e]["paginas_correctas"] = 1
                        else:
                            entities[model_ner][key_e]["paginas_correctas"] = entities[model_ner][key_e]["paginas_correctas"] + 1
                    else:
                        if not "paginas_incorrectas" in entities[model_ner][key_e]:
                            entities[model_ner][key_e]["paginas_incorrectas"] = 1
                        else:
                            entities[model_ner][key_e]["paginas_incorrectas"] = entities[model_ner][key_e]["paginas_incorrectas"] + 1
                    if not "paginas_correctas" in entities[model_ner][key_e]:
                        entities[model_ner][key_e]["porcentaje_paginas_correctas"] = 0
                    elif not "paginas_incorrectas" in entities[model_ner][key_e]:
                        entities[model_ner][key_e]["porcentaje_paginas_correctas"] = 1
                    else:
                        entities[model_ner][key_e]["porcentaje_paginas_correctas"] = (
                            entities[model_ner][key_e]["paginas_correctas"]/
                            (entities[model_ner][key_e]["paginas_correctas"]+entities[model_ner][key_e]["paginas_incorrectas"])
                        )

        for model_ner, values_model in entities.items():
            correct = 0
            incorrect = 0
            correct_pages = 0
            incorrect_pages = 0
            for entitie, value in values_model.items():
                if "entidades_correctas" in value:
                    correct = correct+value["entidades_correctas"]
                if "entidades_incorrectas" in value:
                    incorrect = incorrect+value["entidades_incorrectas"]
                if "paginas_correctas" in value:
                    correct_pages = correct_pages+value["paginas_correctas"]
                if "paginas_incorrectas" in value:
                    incorrect_pages = incorrect_pages+value["paginas_incorrectas"]
            entities[model_ner]["entidades_correctas"] = correct
            entities[model_ner]["entidades_incorrectas"] = incorrect
            entities[model_ner]["paginas_correctas"] = correct_pages
            entities[model_ner]["paginas_incorrectas"] = incorrect_pages
            try:
                entities[model_ner]["porcentaje_entidades_correctas"] = correct/(correct+incorrect)
            except ZeroDivisionError:
                entities[model_ner]["porcentaje_entidades_correctas"] = 1
            try:
                entities[model_ner]["porcentaje_paginas_correctas"] = correct_pages/(correct_pages+incorrect_pages)
            except ZeroDivisionError:
                entities[model_ner]["porcentaje_paginas_correctas"] = 1

        
        percent_correct_entities = total_correct_entities / (total_correct_entities+total_incorrect_entities)
        percent_correct_pages = total_correct_pages / (total_correct_pages+total_incorrect_pages)

        self.resume = { }
        self.resume["creditos_analizados"] = credits_
        self.resume["total_creditos_analizados"] = len(self.tests)
        self.resume["total_entidades_correctas"] = total_correct_entities
        self.resume["total_entidades_incorrectas"] = total_incorrect_entities
        self.resume["total_paginas_correctas"] = total_correct_pages
        self.resume["total_paginas_incorrectas"] = total_incorrect_pages
        self.resume["porcentaje_entidades_correctas"] = percent_correct_entities
        self.resume["porcentaje_paginas_correctas"] = percent_correct_pages
        self.resume["entidades"] = entities

    def save(self):
        prueba_realizada = Prueba_realizada(json.dumps(self.resume))
        self.resume["id_prueba_realizada"] = prueba_realizada.id
        for key, value in self.tests.items():
            Creditos_prueba_realizada(prueba_realizada.id, value["id_credito_testeado"])
        db.session.commit()
        Log.i(__name__, "Todos los modelos han sido almacenados")