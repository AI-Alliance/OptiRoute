from logic.models import Place


def get_place_by_id(places: list, place_id: str) -> Place:
    return next((place for place in places if place.place_id == place_id), None)