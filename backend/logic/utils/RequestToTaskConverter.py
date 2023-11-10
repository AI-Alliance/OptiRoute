from logic import Task, TaskBuilder
import json


class RequestToTaskConverter:
    @staticmethod
    def convert(request_dict: dict) -> Task:
        print("Start request conversion")
        clients_number = request_dict['clientsNumber']
        task = TaskBuilder().set_clients_number(clients_number).get_task()
        print("Request was converted.")
        return task
