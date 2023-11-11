from flask import Flask, abort
from flask import request
from flask import jsonify
from flask_cors import CORS, cross_origin

from logic import Task
from logic import RequestToTaskConverter
from logic import RandomAlgorithm
from services import TaskService
from services.SolutionService import SolutionService

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

solutionService = SolutionService()
taskService = TaskService(solutionService)


@app.route("/")
@cross_origin()
def welcome_page():
    return "<p>Welcome To VRP server</p>"


@app.route("/tasks", methods=['POST'])
@cross_origin()
def submit_task():
    request_dict = request.json
    task = RequestToTaskConverter.convert(request_dict)
    taskService.add(task)
    return ""


@app.route("/tasks", methods=['GET'])
@cross_origin()
def get_all_tasks():
    return jsonify({
        "tasks": list(map(lambda t: t.to_dict(), taskService.get_all()))
    })


@app.route("/solutions", methods=['GET'])
@cross_origin()
def get_solutions():
    return jsonify({
        "solutions": list(map(lambda t: t.to_dict(), solutionService.get_all()))
    })


@app.route('/solutions/<string:task_id>')
@cross_origin()
def get_solution_by_task(task_id):
    solution = solutionService.get_by_task_id(task_id)
    if solution is None:
        abort(404)
    return jsonify(
        solution.to_dict()
    )