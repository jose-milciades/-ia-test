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


@app.route('/download/<path:filename>', methods=['GET', 'POST'])
def download(filename):
    #http://localhost:4503/download/809035316
    directory = "results/reviewed/"+filename+".xlsx"
    return send_file(directory, as_attachment=True)