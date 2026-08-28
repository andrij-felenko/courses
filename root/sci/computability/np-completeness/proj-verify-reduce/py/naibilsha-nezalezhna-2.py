def max_independent(n, edges):
    adj = [set() for _ in range(n)]
    for (u, v) in edges:
        adj[u].add(v); adj[v].add(u)
    best = []
    for mask in range(1 << n):                       # усі 2ⁿ підмножин вершин
        S = [i for i in range(n) if mask & (1 << i)]
        ok = all(v not in adj[u] for a, u in enumerate(S) for v in S[a + 1:])
        if ok and len(S) > len(best):
            best = S
    return best
