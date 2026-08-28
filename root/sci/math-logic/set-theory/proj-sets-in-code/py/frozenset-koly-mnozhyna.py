def powerset_set(xs):
    xs = list(xs)
    n = len(xs)
    result = set()                    # множина, елементами якої будуть множини
    for mask in range(1 << n):
        sub = frozenset(xs[i] for i in range(n) if mask >> i & 1)
        result.add(sub)               # frozenset незмінний → гешовний → лягає
    return result

P = powerset_set({1, 2, 3})
print(len(P))                         # 8   — потужність |P(A)| = 2³
print(frozenset() in P)               # True — порожня множина теж підмножина
print(frozenset({1, 2}) in P)         # True — і {1, 2} серед підмножин
