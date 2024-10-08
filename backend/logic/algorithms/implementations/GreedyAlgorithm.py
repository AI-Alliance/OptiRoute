from logic import Task
from logic.Solution import Solution
from logic.algorithms.Algorithm import Algorithm
from logic.models import Place
from logic.models.Vehicle import Vehicle


class GreedyAlgorithm(Algorithm):
    def solve(self, task: Task) -> Solution:
        depot: Place = task.places[0]
        clients = task.places[1:]
        vehicles: list[Vehicle] = task.vehicles
        unvisited_clients: list[Place] = clients.copy()

        vehicles_id_to_current_capacity = {}
        for vehicle in vehicles:
            vehicles_id_to_current_capacity[vehicle.vehicle_id] = vehicle.capacity

        vehicles_id_to_places_dict = {}

        # starting from depot
        # for vehicle in vehicles:
        #     vehicles_id_to_places_dict[vehicle.vehicle_id] = [depot]
        self.start_in_depo(depot, vehicles, vehicles_id_to_places_dict)
        while len(unvisited_clients) != 0:
            shortest_distance = float('inf')
            best_pair = (None, None)
            for vehicle in vehicles:
                last_place_visited_by_vehicle = vehicles_id_to_places_dict[vehicle.vehicle_id][-1]
                for client in unvisited_clients:
                    possible_distance = task.distance_matrix[last_place_visited_by_vehicle.place_index][
                        client.place_index]
                    if vehicles_id_to_current_capacity[
                        vehicle.vehicle_id] >= client.demand and possible_distance < shortest_distance:
                        best_pair = (vehicle, client)
                        shortest_distance = possible_distance
            if best_pair[0] is not None:
                best_vehicle: Vehicle = best_pair[0]
                best_client: Place = best_pair[1]
                vehicles_id_to_places_dict[best_vehicle.vehicle_id].append(best_client)
                vehicles_id_to_current_capacity[best_vehicle.vehicle_id] -= best_client.demand
                unvisited_clients.remove(best_client)
            else:
                break

        # finishing in depot
        self.finish_in_depo(depot, vehicles,vehicles_id_to_places_dict )
        # for vehicle in vehicles:
        #     route: list = vehicles_id_to_places_dict[vehicle.vehicle_id]
        #     if len(route) <= 1:
        #         vehicles_id_to_places_dict[vehicle.vehicle_id] = []
        #     else:
        #         vehicles_id_to_places_dict[vehicle.vehicle_id].append(depot)


        solution = Solution(task, vehicles_id_to_places_dict)
        print("Problem Solved by greedy algorithms")
        return solution
