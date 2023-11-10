from flask import Flask
from flask import request
from flask import jsonify

from logic import Task
from logic import RequestToTaskConverter
from logic import GreedyAlgorithm

app = Flask(__name__)

@app.route("/")
def hello_world():
    task = Task()
    return "<p>Welcome To VRP server</p>"


@app.route("/submit", methods=['POST'])
def submit_task():
    request_dict = request.json
    task = RequestToTaskConverter.convert(request_dict)
    algorithm = GreedyAlgorithm()
    result = algorithm.solve(task)
    return ""
@app.route("/solutions", methods=['GET'])
def get_solutions():
    return jsonify({
        "results": [
            {
                "result_id": 0,
            },
            {
                "result_id": 2,
            }
        ]
    })