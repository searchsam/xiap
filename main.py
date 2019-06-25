from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route("/", methods=["GET"])
def hello():
    return "Hello World!"


@app.route("/data", methods=["POST"])
def getData():
    print("ruta")
    if request.headers["Content-Type"] == "application/json":
        print(request.json)
        return jsonify(request.json)
    else:
        return jsonify(False), 500
