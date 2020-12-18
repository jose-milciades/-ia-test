from app import app
from flask import jsonify, request, send_from_directory, send_file
import gc
from app.Test import Test
import os
from zipfile import ZipFile
from datetime import datetime
from dotenv import load_dotenv
import json


@app.route("/")
def index():
    return "Working!"


@app.route("/ping")
def ping():
    return "Pong!"


@app.route("/gc")
def garbage_collector():
    gc.collect()
    return "Garbage Collector Called!"


@app.route("/test", methods=["GET", "POST"])
def testing(json_return=True, send_with_correct_text=False):
    test = { }
    t = None
    for credit in request.json.get("creditos"):
        t = Test(credit, send_with_correct_text)
        test[credit] = (json.loads(t.__repr__()))
    if json_return:
        return jsonify(test)
    else:
        return test


@app.route("/test/resumen", methods=["GET", "POST"])
def test_resume():
    tests = testing(False, True)
    total_correct_entities = 0
    total_incorrect_entities = 0
    total_correct_pages = 0
    total_incorrect_pages = 0
    entities = { } 
    credits_ = []
    for key, value in tests.items():
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
                    if not "correctos" in entities[model_ner][key_e]:
                        entities[model_ner][key_e]["correctos"] = 1
                    else:
                        entities[model_ner][key_e]["correctos"] = entities[model_ner][key_e]["correctos"] + 1
                else:
                    if not "incorrectos" in entities[model_ner][key_e]:
                        entities[model_ner][key_e]["incorrectos"] = 1
                    else:
                        entities[model_ner][key_e]["incorrectos"] = entities[model_ner][key_e]["incorrectos"] + 1
                if not "correctos" in entities[model_ner][key_e]:
                    entities[model_ner][key_e]["porcentaje_correcto"] = 0
                elif not "incorrectos" in entities[model_ner][key_e]:
                    entities[model_ner][key_e]["porcentaje_correcto"] = 1
                else:
                    entities[model_ner][key_e]["porcentaje_correcto"] = (
                        entities[model_ner][key_e]["correctos"]/
                        (entities[model_ner][key_e]["correctos"]+entities[model_ner][key_e]["incorrectos"])
                    )

    for model_ner, values_model in entities.items():
        correct = 0
        incorrect = 0
        for entitie, value in values_model.items():
            if "correctos" in value:
                correct = correct+value["correctos"]
            if "incorrectos" in value:
                incorrect = incorrect+value["incorrectos"]
        entities[model_ner]["entidades_correctas"] = correct
        entities[model_ner]["entidades_incorrectas"] = incorrect
        try:
            entities[model_ner]["porcentaje_entidades_correctas"] = correct/(correct+incorrect)
        except ZeroDivisionError:
            entities[model_ner]["porcentaje_entidades_correctas"] = 1

    
    percent_correct_entities = total_correct_entities / (total_correct_entities+total_incorrect_entities)
    percent_correct_pages = total_correct_pages / (total_correct_pages+total_incorrect_pages)

    resume = { }
    resume["creditos_analizados"] = credits_
    resume["total_creditos_analizados"] = len(tests)
    resume["total_entidades_correctas"] = total_correct_entities
    resume["total_entidades_incorrectas"] = total_incorrect_entities
    resume["total_paginas_correctas"] = total_correct_pages
    resume["total_paginas_incorrectas"] = total_incorrect_pages
    resume["porcentaje_entidades_correctas"] = percent_correct_entities
    resume["porcentaje_paginas_correctas"] = percent_correct_pages
    resume["entidades"] = entities
    
    return jsonify(resume)


@app.route('/download/<path:filename>', methods=['GET', 'POST'])
def download(filename):
    #http://localhost:4503/download/809035316
    directory = "results/reviewed/"+filename+".xlsx"
    return send_file(directory, as_attachment=True)