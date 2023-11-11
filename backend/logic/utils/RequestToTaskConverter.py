import numpy as np
from logic import Task, TaskBuilder
from logic.models import Place

from logic.models.Vehicle import Vehicle


class RequestToTaskConverter:
    @staticmethod
    def convert(request_dict: dict) -> Task:
        print("Start request conversion")
        task_id: str = request_dict['task_id']
        rows_list: list = request_dict['rows']
        places_dict_list: list = request_dict['places']
        vehicles_dict_list: list = request_dict['vehicles']
        places = RequestToTaskConverter.get_models_from_dictionary(places_dict_list, Place)
        vehicles = RequestToTaskConverter.get_models_from_dictionary(vehicles_dict_list, Vehicle)
        distance_matrix = RequestToTaskConverter.rows_list_to_distance_matrix(rows_list)

        task = TaskBuilder() \
            .set_id(task_id)\
            .set_distance_matrix(distance_matrix) \
            .set_places(places)\
            .set_vehicles(vehicles)\
            .get_task()
        print("Request was converted.")
        return task

    @staticmethod
    def rows_list_to_distance_matrix(rows_list: list):
        size = len(rows_list)
        matrix = np.zeros((size, size))
        print(f"Row list:{rows_list}")
        for i in range(size):
            elements = rows_list[i]['elements']
            for j in range(size):
                element = elements[j]
                matrix[i][j] = element
        print(f"Matrix:{matrix}")
        return matrix

    @staticmethod
    def get_models_from_dictionary(models_dict_list: list, model_class):
        models = []
        size = len(models_dict_list)
        for i in range(size):
            place_dict = models_dict_list[i]
            models.append(model_class.create_from_dict(place_dict))
        return models
