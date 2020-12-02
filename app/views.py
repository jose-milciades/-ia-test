from app import app
from flask import jsonify, request, send_from_directory, send_file
import gc
from app.Test import Test
import os
from zipfile import ZipFile
from datetime import datetime


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
def testing(json=True, send_with_correct_text=False):
    test = { }
    for credit in request.json.get("creditos"):
        t = Test(None, credit, send_with_correct_text)
        test[credit] = (t.make_test(True))
    if json:
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
        for key_e, value_e in value["entidades"].items():
            if not key_e in entities:
                entities[key_e] = { }
            if value_e["texto_es_correcto"]:
                if not "correctos" in entities[key_e]:
                    entities[key_e]["correctos"] = 1
                else:
                    entities[key_e]["correctos"] = entities[key_e]["correctos"] + 1
            else:
                if not "incorrectos" in entities[key_e]:
                    entities[key_e]["incorrectos"] = 1
                else:
                    entities[key_e]["incorrectos"] = entities[key_e]["incorrectos"] + 1
            if not "correctos" in entities[key_e]:
                entities[key_e]["porcentaje_correcto"] = 0
            elif not "incorrectos" in entities[key_e]:
                entities[key_e]["porcentaje_correcto"] = 1
            else:
                entities[key_e]["porcentaje_correcto"] = entities[key_e]["correctos"]/(entities[key_e]["correctos"]+entities[key_e]["incorrectos"])
    
    percent_correct_entities = total_correct_entities / (total_correct_entities+total_incorrect_entities)
    percent_correct_pages = total_correct_pages / (total_correct_pages+total_incorrect_pages)

    resume = { }
    resume["creditos_analizados"] = credits_
    resume["total_creditos_analizados"] = len(tests)
    resume["total_entidades_correctad"] = total_correct_entities
    resume["total_entidades_incorrectas"] = total_incorrect_entities
    resume["total_paginas_correctas"] = total_correct_pages
    resume["total_paginas_incorrectas"] = total_incorrect_pages
    resume["porcentaje_entidades_correctas"] = percent_correct_entities
    resume["porcentaje_paginas_correctas"] = percent_correct_pages
    resume["entidades_incorrectas"] = entities
    
    return jsonify(resume)


@app.route('/download/<path:filename>', methods=['GET', 'POST'])
def download(filename):
    #http://localhost:4503/download/809035316
    directory = "results/reviewed/"+filename+".xlsx"
    return send_file(directory, as_attachment=True)