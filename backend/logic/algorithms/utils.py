from operator import itemgetter


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


def copy(array):
    n_array = [x.copy() for x in array]
    return n_array


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