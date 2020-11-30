from app import app
from flask import jsonify, request
import gc


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
    if "correct_text" in request.json.keys():
        correct_text = request.json.get("correct_text")
        del request.json["correct_text"]
    else: 
        correct_text = False
    request_ner = RequestNer(request.json)
    response_ner = ResponseNer(request_ner.__dict__)
    
    return jsonify(response_ner.json_response(correct_text=correct_text))
