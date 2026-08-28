from collections import deque

class DinicPython:
    def __init__(self, n: int):
        self.n = n
        self.adj = [[] for _ in range(n)]
        self.level = [-1] * n
        self.ptr = [0] * n

    def add_edge(self, u: int, v: int, cap: int, rev_cap: int = 0):
        if u == v:
            return
        # Структура запису: [to, rev_index, capacity, flow]
        forward = [v, len(self.adj[v]), cap, 0]
        backward = [u, len(self.adj[u]), rev_cap, 0]
        self.adj[u].append(forward)
        self.adj[v].append(backward)

    def bfs(self, s: int, t: int) -> bool:
        self.level = [-1] * self.n
        self.level[s] = 0
        q = deque([s])

        while q:
            u = q.popleft()
            for to, rev, cap, flow in self.adj[u]:
                if cap - flow > 0 and self.level[to] == -1:
                    self.level[to] = self.level[u] + 1
                    q.append(to)
        return self.level[t] != -1

    def dfs(self, u: int, t: int, pushed: int) -> int:
        if pushed == 0 or u == t:
            return pushed

        for cid in range(self.ptr[u], len(self.adj[u])):
            self.ptr[u] = cid
            to, rev, cap, flow = self.adj[u][cid]
            if self.level[u] + 1 != self.level[to] or cap - flow == 0:
                continue

            tr = self.dfs(to, t, min(pushed, cap - flow))
            if tr == 0:
                continue

            self.adj[u][cid][3] += tr
            self.adj[to][rev][3] -= tr
            return tr
        return 0

    def max_flow(self, s: int, t: int) -> int:
        total_flow = 0
        while self.bfs(s, t):
            self.ptr = [0] * self.n
            while True:
                pushed = self.dfs(s, t, float('inf'))
                if pushed == 0:
                    break
                total_flow += pushed
        return total_flow
