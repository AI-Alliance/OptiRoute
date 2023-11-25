from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

from logic import Task
from logic.Solution import Solution
from logic.SolutionStatus import SolutionStatus
from logic.algorithms.Algorithm import Algorithm
from logic.models import Place
from logic.models.Vehicle import Vehicle


class GoogleAlgorithm(Algorithm):
    def solve(self, task: Task) -> Solution:
        """Entry point of the program."""
        # Instantiate the data problem.
        demands = [place.demand for place in task.places]
        vehicle_capacities = [vehicle.capacity for vehicle in task.vehicles]
        data = self.create_data_model(task.distance_matrix,
                                      num_vehicles=len(task.vehicles),
                                      demands=demands,
                                      vehicle_capacities=vehicle_capacities
                                      )

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


        def demand_callback(from_index):
            """Returns the demand of the node."""
            # Convert from routing variable Index to demands NodeIndex.
            from_node = manager.IndexToNode(from_index)
            return data["demands"][from_node]

        demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)

        self.add_capacity_constraint(data, demand_callback_index, routing)


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
            return Solution(task, vehicles_id_to_places_dict, status=SolutionStatus.FAILED)

        return Solution(task, vehicles_id_to_places_dict)

    def add_capacity_constraint(self, data, demand_callback_index, routing):
        routing.AddDimensionWithVehicleCapacity(
            demand_callback_index,
            0,  # null capacity slack
            data["vehicle_capacities"],  # vehicle maximum capacities
            True,  # start cumul to zero
            "Capacity",
        )

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
        search_parameters.local_search_metaheuristic = (
            routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
        )
        search_parameters.time_limit.FromSeconds(1)
        return search_parameters

    def add_distance_constraint(self, routing, transit_callback_index):
        dimension_name = "Distance"
        routing.AddDimension(
            transit_callback_index,
            0,  # no slack
            100_000_000_000,  # vehicle maximum travel distance
            True,  # start cumul to zero
            dimension_name,
        )
        distance_dimension = routing.GetDimensionOrDie(dimension_name)
        distance_dimension.SetGlobalSpanCostCoefficient(100)

    def create_routing_index_manager(self, data):
        return pywrapcp.RoutingIndexManager(
            len(data["distance_matrix"]), data["num_vehicles"], data["depot"]
        )

    def create_data_model(self, distance_matrix, num_vehicles, demands, vehicle_capacities):
        """Stores the data for the problem."""
        data = {}
        data["distance_matrix"] = (distance_matrix.astype(int)).tolist()

        # distance_matrix.tolist()
        print(distance_matrix.tolist())
        data["num_vehicles"] = num_vehicles
        data["depot"] = 0
        data["demands"] = demands
        data["vehicle_capacities"] = vehicle_capacities
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
        total_distance = 0
        total_load = 0
        for vehicle_id in range(data["num_vehicles"]):
            index = routing.Start(vehicle_id)
            plan_output = f"Route for vehicle {vehicle_id}:\n"
            route_distance = 0
            route_load = 0
            while not routing.IsEnd(index):
                node_index = manager.IndexToNode(index)
                route_load += data["demands"][node_index]
                plan_output += f" {node_index} Load({route_load}) -> "
                previous_index = index
                index = solution.Value(routing.NextVar(index))
                route_distance += routing.GetArcCostForVehicle(
                    previous_index, index, vehicle_id
                )
            plan_output += f" {manager.IndexToNode(index)} Load({route_load})\n"
            plan_output += f"Distance of the route: {route_distance}m\n"
            plan_output += f"Load of the route: {route_load}\n"
            print(plan_output)
            total_distance += route_distance
            total_load += route_load
        print(f"Total distance of all routes: {total_distance}m")
        print(f"Total load of all routes: {total_load}")
