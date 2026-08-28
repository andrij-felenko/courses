# Python Implementation: Object-Oriented Kuhn's Matching Solver
from typing import List, Tuple

class BipartiteMatchingKuhn:
    def __init__(self, n_left: int, n_right: int):
        self.n1 = n_left
        self.n2 = n_right
        self.adj: List[List[int]] = [[] for _ in range(n_left)]

    def add_edge(self, u_left: int, v_right: int) -> None:
        self.adj[u_left].append(v_right)

    def find_max_matching(self) -> List[Tuple[int, int]]:
        """
        Знаходить максимальне двочасткове паросполучення.
        Повертає список пар вершин (u_left, v_right).
        """
        match_v = [-1] * self.n2

        def try_augment(u: int, visited: List[bool]) -> bool:
            if visited[u]:
                return False
            visited[u] = True

            for v in self.adj[u]:
                if match_v[v] == -1 or try_augment(match_v[v], visited):
                    match_v[v] = u
                    return True
            return False

        for u in range(self.n1):
            visited = [False] * self.n1
            try_augment(u, visited)

        return [(u, v) for v, u in enumerate(match_v) if u != -1]
