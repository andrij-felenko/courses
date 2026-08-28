class DSU:
    def __init__(self, n: int):
        self.parent = list(range(n))     # кожен — сам собі корінь
        self.rank = [0] * n

    def find(self, x: int) -> int:
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]  # стиснення шляху
            x = self.parent[x]
        return x

    def unite(self, a: int, b: int) -> None:             # злити два ланцюги
        a, b = self.find(a), self.find(b)
        if a == b:
            return
        if self.rank[a] < self.rank[b]:
            a, b = b, a
        self.parent[b] = a
        if self.rank[a] == self.rank[b]:
            self.rank[a] += 1
