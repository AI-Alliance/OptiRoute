# from logic import Task
# from logic.models.Place import Place
# from logic.Solution import Solution
# from logic.algorithms.Algorithm import Algorithm
#
# from logic.algorithms.utils import IterPairs, DistanceMapper, CMapBuildAlgorithm
# from operator import attrgetter
# import random
#
# class RouteWithLabel:
#     def __init__(self, feasibility, cost, route):
#         self.feasibility = feasibility
#         self.cost = cost
#         self.route = route
#
#     def __repr__(self):
#         return repr((self.feasibility, self.cost, self.route))
#
#
# def select_in_m(m):
#     n = random.random()
#     size = len(m)
#     c = 0
#     for i in range(size):
#         c += 2 * (size + 1 - (i + 1)) / (size * (size + 1))
#         if n <= c:
#             return m[i]
#     return m[size - 1]
#
#
# class AdaptiveMemoryTabuSearch(Algorithm):
#     AMP_iter = 10  # number of AMP iterations
#     I = 5 # number of initial solution in Memory
#     use_capacity = True
#
#     def __init__(self):
#         super().__init__()
#         self.M = []
#
#
#     def solve(self, task: Task) -> Solution:
#         self.depot: Place = task.places[0]
#         self.clients: list[Place] = task.places[1:]
#         self.vehicles = task.vehicles
#         self.distances = task.distance_matrix
#         self.client_ids = [c.place_index - 1 for c in self.clients]
#         vehicles_to_places_dict = {}
#
#         if len(self.vehicles) == 0:
#             solution = Solution(task, vehicles_to_places_dict)
#             print("No vehicles!")
#             return solution
#
#         # starting from depot
#         self.start_in_depo(self.depot, self.vehicles, vehicles_to_places_dict)
#
#         # initial solution
#         self.dm = DistanceMapper(self.clients, self.distances)
#         self.cmap, self.smap = self.dm.map_closest()
#         self.s0 = self.initial()
#
#         # calculate solution
#         best = self.search()
#
#         if not self.feasible: # !!!!!!!!
#             best = [[] for x in self.vehicles]
#
#         if self.feasible:
#             for route, vehicle in zip(best, self.vehicles):
#                 for r in route:
#                     place: Place = self.clients[r]
#                     vehicles_to_places_dict[vehicle.vehicle_id].append(place)
#
#         # finishing in depot
#         self.finish_in_depo(self.depot, self.vehicles, vehicles_to_places_dict)
#
#         solution = Solution(task, vehicles_to_places_dict)
#
#         print("Problem Solved by Tabu!")
#         return solution
#
#
#     def initial(self):
#         build_algo = CMapBuildAlgorithm(self.vehicles, self.clients, self.cmap)
#         for i in range(self.I):
#             s = build_algo.make_initial()
#
#             # if self.USE_INITIAL_TABU_SEARCH and len(s) != 0:
#             #     TS = TabuSearch(use_capacity=True, capacity=self.max_capacity)
#             #     TS.load_data(self.customers, self.points)
#             #     TS.initial(s)
#             #     s = TS.search()
#
#             self.add_to_memory(s)
#         self.M.sort(key=attrgetter('feasibility', 'cost'), reverse=True)
#
#
#     def add_to_memory(self, s):
#         # f = self.check_feasibility(s)
#         f = 1  # TODO make TS make feasible solutions or something
#         c = -self.check_cost(s)
#         for r in s:
#             if len(r) == 0:
#                 continue
#             self.M.append(RouteWithLabel(f, c, r))
#
#     def check_cost(self, solution):
#         if len(solution) == 0:
#             return 0
#         weight = 0
#         for vehicle_ind, route in enumerate(solution):
#             if len(route) == 0:
#                 continue
#             u = route[0]
#             weight += self.get_distance(self.depot, self.clients[u])
#             for node in route[1:]:
#                 weight += self.get_distance(self.clients[u], self.clients[node])
#                 u = node
#             weight += self.get_distance(self.clients[u], self.depot)
#         return weight
#
#     # def fitness(self, solution):
#     #     if len(solution) == 0:
#     #         return 0
#     #     weight = 0
#     #     cap_overload = 0
#     #     for vehicle_ind, route in enumerate(solution):
#     #         if len(route) == 0:
#     #             continue
#     #         u = route[0]
#     #         weight += self.get_distance(self.depot, self.clients[u])
#     #         for node in route[1:]:
#     #             weight += self.get_distance(self.clients[u], self.clients[node])
#     #             u = node
#     #         weight += self.get_distance(self.clients[u], self.depot)
#     #         cap_overload += self.calc_capacity(route, self.vehicles[vehicle_ind].capacity)
#     #     if cap_overload > 0:
#     #         self.feasible = False
#     #     else:
#     #         self.feasible = True
#     #     return weight + weight * cap_overload * self.CAP_OVERLOAD_PENALTY
#
#     def calc_capacity(self, route, capacity):
#         if not self.use_capacity:
#             return 0
#         current_capacity = 0
#         for v in route:
#             current_capacity += self.get_demand(v)
#         if current_capacity > capacity:
#             return current_capacity - capacity
#         return 0
#
#     def check_capacity_valid(self, route, capacity):
#         return self.calc_capacity(route, capacity) <= 0
#
#     def get_demand(self, v):
#         return self.clients[v].demand
#
#     def get_distance(self, place_u, place_v) -> int:
#         return self.distances[place_u.place_index][place_v.place_index]
#
#     def construct_solution(self):
#         temp_m = self.M.copy()
#         solution = []
#         unrouted_clients = set(self.client_ids)
#         while len(temp_m) > 0:
#             r = select_in_m(temp_m)
#             solution.append(r.route)
#             for c in r.route:
#                 unrouted_clients.remove(c)
#             del_routes = []
#             for route in temp_m:
#                 if any(x in r.route for x in route.route):
#                     del_routes.append(route)
#             for dr in del_routes:
#                 temp_m.remove(dr)
#         if len(unrouted_clients) > 0:
#             build_algo = CMapBuildAlgorithm(self.vehicles, self.clients, self.cmap)
#             sla.clients = list(unrouted_clients)
#             sla.points = self.points
#             sol = sla.sweep()
#             for s in sol:
#                 solution.append(s)
#         return solution
#
#     def search(self):
#         best_sol_global = []
#         best_fit_global = 99999
#         for i in range(self.AMP_iter):
#             s = self.construct_solution()
#             if len(s) != 0:
#                 TS = TabuSearch(use_capacity=True, capacity=self.max_capacity)
#                 TS.load_data(self.customers, self.points)
#                 TS.initial(s)
#                 bs = TS.search()
#                 bc = TS.get_best_cost()
#                 if bc < best_fit_global:
#                     best_sol_global = bs
#                     best_fit_global = bc
#                 self.add_to_memory(bs)
#             self.M.sort(key=attrgetter('feasibility', 'cost'), reverse=True)
#         return best_sol_global
