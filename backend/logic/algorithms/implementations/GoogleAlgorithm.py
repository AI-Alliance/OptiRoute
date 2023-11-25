from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

from logic import Task
from logic.Solution import Solution
from logic.algorithms.Algorithm import Algorithm
from logic.models import Place
from logic.models.Vehicle import Vehicle


class GoogleAlgorithm(Algorithm):
    def solve(self, task: Task) -> Solution:
        """Entry point of the program."""
        # Instantiate the data problem.
        data = self.create_data_model(task.distance_matrix)

        # Create the routing index manager.
        manager = self.create_routing_index_manager(data)

        # Create Routing Model.
        routing = pywrapcp.RoutingModel(manager)

        # Create and register a transit callback.
        def distance_callback(from_index, to_index):
            """Returns the distance between the two nodes."""
            # Convert from routing variable Index to distance matrix NodeIndex.
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return data["distance_matrix"][from_node][to_node]

        transit_callback_index = routing.RegisterTransitCallback(distance_callback)

        # Define cost of each arc.
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

        # Add Distance constraint.
        self.add_distance_constraint(routing, transit_callback_index)

        # Setting first solution heuristic.
        search_parameters = self.setting_first_solution_heuristic()

        # Solve the problem.
        google_solution = routing.SolveWithParameters(search_parameters)

        vehicles_id_to_places_dict = {}
        # Print solution on console.
        if google_solution:
            self.print_solution(data, manager, routing, google_solution)
            vehicle_index_to_places_index = self.get_vehicle_index_to_places_index(data, manager, routing, google_solution)
            vehicles_id_to_places_dict = self.get_vehicles_id_to_places_dict(vehicle_index_to_places_index, task.vehicles, task.places)
        else:
            print("No solution found !")

        return Solution(task, vehicles_id_to_places_dict)
    def get_vehicles_id_to_places_dict(self,vehicle_index_to_places_index:dict, vehicles:list[Vehicle], places:list[Place]):
        vehicles_id_to_places_dict = {}
        for vehicle_index, places_indexes in vehicle_index_to_places_index.items():
            print(places_indexes)
            vehicles_id_to_places_dict[vehicles[vehicle_index].vehicle_id] = [places[place_index] for place_index in places_indexes]
        return vehicles_id_to_places_dict
    def setting_first_solution_heuristic(self):
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
        )
        return search_parameters

    def add_distance_constraint(self, routing, transit_callback_index):
        dimension_name = "Distance"
        routing.AddDimension(
            transit_callback_index,
            0,  # no slack
            3000,  # vehicle maximum travel distance
            True,  # start cumul to zero
            dimension_name,
        )
        distance_dimension = routing.GetDimensionOrDie(dimension_name)
        distance_dimension.SetGlobalSpanCostCoefficient(100)

    def create_routing_index_manager(self, data):
        return pywrapcp.RoutingIndexManager(
            len(data["distance_matrix"]), data["num_vehicles"], data["depot"]
        )

    def create_data_model(self, distance_matrix):
        """Stores the data for the problem."""
        data = {}
        data["distance_matrix"] = (distance_matrix.astype(int)).tolist()

        # distance_matrix.tolist()
        print(distance_matrix.tolist())
        data["num_vehicles"] = 2
        data["depot"] = 0
        return data

    def get_vehicle_index_to_places_index(self, data,  manager, routing, solution):
        vehicle_index_to_places_index = {}
        for vehicle_index in range(data["num_vehicles"]):
            places_index = []
            index = routing.Start(vehicle_index)
            while not routing.IsEnd(index):
                place_index = manager.IndexToNode(index)
                places_index.append(place_index)
                index = solution.Value(routing.NextVar(index))
            # return to depo
            places_index.append(0)
            vehicle_index_to_places_index[vehicle_index] = places_index
        return vehicle_index_to_places_index


    def print_solution(self, data, manager, routing, solution):
        """Prints solution on console."""
        print(f"Objective: {solution.ObjectiveValue()}")
        max_route_distance = 0
        for vehicle_id in range(data["num_vehicles"]):
            index = routing.Start(vehicle_id)
            plan_output = f"Route for vehicle {vehicle_id}:\n"
            route_distance = 0
            while not routing.IsEnd(index):
                plan_output += f" {manager.IndexToNode(index)} -> "
                previous_index = index
                index = solution.Value(routing.NextVar(index))
                route_distance += routing.GetArcCostForVehicle(
                    previous_index, index, vehicle_id
                )

            plan_output += f"{manager.IndexToNode(index)}\n"
            plan_output += f"Distance of the route: {route_distance}m\n"
            print(plan_output)
            max_route_distance = max(route_distance, max_route_distance)
        print(f"Maximum of the route distances: {max_route_distance}m")
