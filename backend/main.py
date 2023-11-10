from flask import Flask
from flask import request
from flask import jsonify

from logic import Task
from logic import RequestToTaskConverter
from logic import GreedyAlgorithm
from services import TaskService
from services.SolutionService import SolutionService

app = Flask(__name__)

taskService = TaskService()
solutionService = SolutionService()

@app.route("/")
def welcome_page():
    task = Task()
    return "<p>Welcome To VRP server</p>"


@app.route("/submit", methods=['POST'])
def submit_task():
    request_dict = request.json
    task = RequestToTaskConverter.convert(request_dict)
    taskService.add(task)
    return ""


@app.route("/tasks", methods=['GET'])
def get_all_tasks():
    return jsonify({
        "tasks": list(map(lambda t: t.to_dict(), taskService.get_all()))
    })


@app.route("/solutions", methods=['GET'])
def get_solutions():
    return jsonify({
        "solutions": list(map(lambda t: t.to_dict(), solutionService.get_all()))
    })
