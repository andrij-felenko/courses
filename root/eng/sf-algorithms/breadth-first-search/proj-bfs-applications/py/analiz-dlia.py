from collections import deque

def is_bipartite_python(adj: list[list[int]]) -> bool:
    n = len(adj)
    color = [0] * n

    for start in range(n):
        if color[start] != 0:
            continue

        q = deque([start])
        color[start] = 1

        while q:
            u = q.popleft()
            for v in adj[u]:
                if color[v] == 0:
                    color[v] = 3 - color[u]
                    q.append(v)
                elif color[v] == color[u]:
                    return False
    return True
