from flask import Flask
from logic import Task

app = Flask(__name__)


@app.route("/")
def hello_world():
    task = Task()
    return "<p>Welcome To VRP server</p>"


@app.route("/submit")
def submit_task():
    return "You wanna submit task?"
