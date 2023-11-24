from logic.models import Place


def get_place_by_id(places: list, place_id: str) -> Place:
    return next((place for place in places if place.place_id == place_id), None)


def calculate_distance(distance_matrix, place1: Place, place2: Place):
    return distance_matrix[place1.place_index][place2.place_index]