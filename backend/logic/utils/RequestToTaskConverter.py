import numpy as np
from logic import Task, TaskBuilder


class RequestToTaskConverter:
    @staticmethod
    def convert(request_dict: dict) -> Task:
        print("Start request conversion")
        clients_number = request_dict['clientsNumber']
        vehicles_number = request_dict['vehiclesNumber']
        rows_list: list = request_dict['rows']
        distance_matrix = RequestToTaskConverter.rows_list_to_distance_matrix(rows_list, clients_number)
        task = TaskBuilder() \
            .set_clients_number(clients_number) \
            .set_vehicles_number(vehicles_number) \
            .set_distance_matrix(distance_matrix) \
            .get_task()
        print("Request was converted.")
        return task

    @staticmethod
    def rows_list_to_distance_matrix(rows_list: list, clients_number: int):
        matrix = np.zeros((clients_number, clients_number))
        print(f"Row list:{rows_list}")
        for i in range(len(rows_list)):
            elements = rows_list[i]['elements']
            for j in range(len(elements)):
                element = elements[j]
                matrix[i][j] = element
        print(f"Matrix:{matrix}")
        return matrix
