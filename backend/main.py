from flask import Flask
from flask import request

from logic import Task
from logic import RequestToTaskConverter

app = Flask(__name__)

@app.route("/")
def hello_world():
    task = Task()
    return "<p>Welcome To VRP server</p>"


@app.route("/submit", methods=['POST'])
def submit_task():
    request_dict = request.json
    RequestToTaskConverter.convert(request_dict)
    return ""
