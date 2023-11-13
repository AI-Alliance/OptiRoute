
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
