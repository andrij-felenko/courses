class VF2Matcher:
    def __init__(self, g1_adj, g2_adj):
        self.g1 = g1_adj
        self.g2 = g2_adj
        self.n = len(g1_adj)
        self.core1 = [-1] * self.n
        self.core2 = [-1] * self.n

    def is_feasible(self, u, v):
        for other1 in range(self.n):
            if self.g1[u][other1]:
                other2 = self.core1[other1]
                if other2 != -1 and not self.g2[v][other2]:
                    return False
        for other2 in range(self.n):
            if self.g2[v][other2]:
                other1 = self.core2[other2]
                if other1 != -1 and not self.g1[u][other1]:
                    return False
        return True

    def match(self, depth=0):
        if depth == self.n:
            return True

        u = self.core1.index(-1)
        for v in range(self.n):
            if self.core2[v] == -1 and self.is_feasible(u, v):
                self.core1[u] = v
                self.core2[v] = u

                if self.match(depth + 1):
                    return True

                self.core1[u] = -1
                self.core2[v] = -1
        return False

def check_isomorphism(g1, g2):
    if len(g1) != len(g2):
        return None
    matcher = VF2Matcher(g1, g2)
    if matcher.match():
        return matcher.core1
    return None

if __name__ == "__main__":
    g1 = [
        [False, True,  False, True],
        [True,  False, True,  False],
        [False, True,  False, True],
        [True,  False, True,  False]
    ]
    g2 = [
        [False, True,  False, True],
        [True,  False, True,  False],
        [False, True,  False, True],
        [True,  False, True,  False]
    ]
    res = check_isomorphism(g1, g2)
    print("Мапінг VF2:", res)
