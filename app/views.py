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


@app.route("/testing", methods=["GET", "POST"])
def testing():
    test = { }
    for credit in request.json.get("creditos"):
        t = Test(None, credit)
        test[credit] = (t.make_test(True))
    
    return jsonify(test)

@app.route('/download/<path:filename>', methods=['GET', 'POST'])
def download(filename):
    #http://localhost:4503/download/809035316
    directory = "results/reviewed/"+filename+".xlsx"
    return send_file(directory, as_attachment=True)