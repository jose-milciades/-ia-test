from app import app
from flask import jsonify, request, send_from_directory, send_file
import gc
from app.Test import Test
from app.Test_resume import Test_resume
import os
from zipfile import ZipFile
from datetime import datetime
from dotenv import load_dotenv
import json
from app.Compare import Compare
from app.models.Datos_comparacion import Datos_comparacion


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
    resume = Test_resume(tests)

    return jsonify(resume.resume)


@app.route('/test/download/credito/testeado/<path:id_credito_testeado>', methods=['GET', 'POST'])
def download_credito_testeado(id_credito_testeado):
    success = False
    try:
        t = Test(None, True, id_credito_testeado=id_credito_testeado)
        directory = t.save_in_excel(None, None)[4:]
        success = True
        return send_file(directory, as_attachment=True)
    finally:
        if success:
            t.delete_temp()


@app.route('/test/download/datos_comparacion/<path:credito>', methods=['GET', 'POST'])
def download_datos_comparacion(credito):
    try:
        datos_comparacion = Datos_comparacion.query.filter_by(credito=credito).first()
        directory = datos_comparacion.save_in_excel()[4:]
        print("hola")
        return send_file(directory, as_attachment=True)
    finally:
        datos_comparacion.delete_temp()


@app.route('/test/get_creditos_by_id', methods=['POST'])
def get_credito_by_id(json_return=True):
    test = { }
    t = None
    for id in request.json.get("ids"):
        t = Test(None, True, id_credito_testeado=id)
        test[str(t.credito_testeado.credito)+"-"+str(id)] = (json.loads(t.__repr__()))
    if json_return:
        return jsonify(test)
    else:
        return test


@app.route("/test/get_prueba_realizada_by_id/<path:id>", methods=["GET"])
def get_prueba_realizada_by_id(id, json_return=True):
    resume = Test_resume(None, id_prueba_realizada=id)
    if json_return:
        return jsonify(resume.resume)
    else:
        return resume


@app.route("/test/compare_resumen/<path:old_id>/<path:new_id>", methods=["GET"])
def compare_resumen(old_id, new_id):
    old_resume = get_prueba_realizada_by_id(old_id, json_return=False)
    new_resume = get_prueba_realizada_by_id(new_id, json_return=False)
    resume = Compare(old_resume, new_resume)

    return jsonify(resume.resume)


@app.route("/test/upload_data", methods=["GET", "POST"])
def upload_data_for_compare():
    f = request.files.get('file')
    if (f.filename[-4:]=="xlsx"):
        Datos_comparacion(f.filename[:-5], None, f)

    return jsonify("Dato almacenado correctamente")