from flask import Flask, jsonify
import json

app = Flask(__name__)


@app.route('/')
def hello():
    return jsonify('Hello World!')


@app.route('/data/<string:serialnum>/<string:uuid>')
def getData(serialnum, uuid):
    data = dict()
    data['serialnum'] = serialnum
    data['uuid'] = uuid
    with open('data.json', 'w') as outfile:
        json.dump(data, outfile)
    return 'Serial Number: {0} <br> UUID: {1}'.format(serialnum, uuid)
