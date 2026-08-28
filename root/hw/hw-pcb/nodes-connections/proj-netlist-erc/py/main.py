from collections import defaultdict

# Система неперетинних множин зі стисненням шляхів і об'єднанням за рангом.
class DSU:
    def __init__(self, n):
        self.parent = list(range(n))   # makeset: кожен пін — сам собі корінь
        self.rank = [0] * n

    def find(self, x):                 # корінь множини піна x
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]   # зі стисненням
            x = self.parent[x]
        return x

    def unite(self, a, b):             # злити два ланцюги в один
        a, b = self.find(a), self.find(b)
        if a == b:
            return
        if self.rank[a] < self.rank[b]:
            a, b = b, a
        self.parent[b] = a
        if self.rank[a] == self.rank[b]:
            self.rank[a] += 1

# Кожен дріт, крапка-з'єднання й однакова мітка дають по виклику unite():
dsu = DSU(pin_count)
for a, b in wires:                     # дроти й крапки
    dsu.unite(a, b)
for g in named_nets:                   # мітки-імена
    for p in g:
        dsu.unite(g[0], p)

# find(корінь) для кожного піна — і піни з однаковим коренем складають один ланцюг.
nets = defaultdict(list)
for p in range(pin_count):
    nets[dsu.find(p)].append(p)
