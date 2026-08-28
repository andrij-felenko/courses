from collections import deque

# Три матриці Барнінґа–Голла — діють на стовпчик (a, b, c)ᵀ.
A = (( 1, -2, 2), ( 2, -1, 2), ( 2, -2, 3))
B = (( 1,  2, 2), ( 2,  1, 2), ( 2,  2, 3))
C = ((-1,  2, 2), (-2,  1, 2), (-2,  2, 3))

def times(M, t):
    a, b, c = t
    return tuple(r[0] * a + r[1] * b + r[2] * c for r in M)

def primitive_tree(limit):
    """Усі примітивні трійки з c ≤ limit — обхід дерева від (3, 4, 5)."""
    if limit < 5:
        return
    q = deque([(3, 4, 5)])
    while q:
        a, b, c = q.popleft()
        yield (min(a, b), max(a, b), c)
        for M in (A, B, C):
            child = times(M, (a, b, c))
            if child[2] <= limit:            # гіпотенуза дитини завжди більша за батькову
                q.append(child)
