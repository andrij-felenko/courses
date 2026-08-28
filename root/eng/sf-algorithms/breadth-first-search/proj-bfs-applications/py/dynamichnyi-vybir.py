from collections import deque

def bidirectional_bfs_python(adj: list[list[int]], start: int, target: int) -> int:
    if start == target:
        return 0
    n = len(adj)

    dist_f, dist_b = [-1] * n, [-1] * n
    q_f, q_b = deque([start]), deque([target])
    dist_f[start], dist_b[target] = 0, 0

    while q_f and q_b:
        u_f = q_f.popleft()
        for v in adj[u_f]:
            if dist_b[v] != -1:
                return dist_f[u_f] + 1 + dist_b[v]
            if dist_f[v] == -1:
                dist_f[v] = dist_f[u_f] + 1
                q_f.append(v)

        u_b = q_b.popleft()
        for v in adj[u_b]:
            if dist_f[v] != -1:
                return dist_b[u_b] + 1 + dist_f[v]
            if dist_b[v] == -1:
                dist_b[v] = dist_b[u_b] + 1
                q_b.append(v)

    return -1
