from operator import itemgetter
from logic.models.Place import Place
import random

class IterPairs:
    """ odpowiednik pętli
    for (i=0; i<n; i++)
        for (j=i; j<n; j++)
    """
    def __init__(self, n=0):
        self.n = n

    def __iter__(self):
        self.i = 0
        self.j = -1
        return self

    def __next__(self):
        self.j += 1
        if self.j == self.n:
            self.i += 1
            self.j = self.i
        if self.i == self.n:
            raise StopIteration
        return self.i, self.j


def copy_refs(array):
    n_array = [x.copy() for x in array]
    return n_array

def hash_solution(hlist: list):
    return tuple([tuple(x) for x in hlist])


class DistanceMapper:
    def __init__(self, clients, distances):
        self.clients = clients
        self.distances = distances
        self.cmap = None
        self.smap = None

    def get_distance(self, place_u, place_v) -> int:
        return self.distances[place_u.place_index][place_v.place_index]

    def map_closest(self):
        cmap = {}
        smap = {}
        for ci in self.clients:
            p = []
            for cj in self.clients:
                if ci.place_index == cj.place_index:
                    continue
                p.append((self.get_distance(ci, cj), cj))
            p.sort(key=itemgetter(0))
            for i, (d, cj) in enumerate(p):
                smap.update({(ci.place_index,cj.place_index): i})
            cmap.update({ci.place_index: p})
        self.cmap = cmap
        self.smap = smap
        return cmap, smap


class CMapBuildAlgorithm: # Nearest Neighbor build heuristic
    def __init__(self, vehicles, clients, cmap):
        self.vehicles = vehicles.copy()
        self.clients: list[Place] = clients.copy()
        self.cmap: dict = cmap

    def make_initial(self):
        s0 = [[] for _ in self.vehicles]
        visited = []
        for v_i, vehicle in enumerate(self.vehicles):
            if len(self.clients) == 0:
                break
            cap = 0
            c = random.choice(self.clients)
            s0[v_i].append(c.place_index - 1)
            visited.append(c)
            cap += c.demand
            closest = self.cmap[c.place_index]
            self.clients.remove(c)
            for distance, node in closest:
                if cap > vehicle.capacity:
                    break
                if node not in visited:
                    s0[v_i].append(node.place_index - 1)
                    visited.append(node)
                    cap += node.demand
                    self.clients.remove(node)
        return s0