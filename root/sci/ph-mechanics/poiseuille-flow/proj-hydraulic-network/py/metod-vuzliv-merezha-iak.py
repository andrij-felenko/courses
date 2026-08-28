def solve_network(pipes, pressures):
    """pipes: список (u, v, R) — труба між вузлами u,v з опором R (напрям байдужий).
    pressures: {вузол: тиск} — ЗАДАНІ (граничні) тиски: джерела й стоки.
    Повертає (p, Q): p[вузол] — тиск у кожному вузлі; Q[(u,v)] — витрата з u в v."""
    nodes = set(pressures)
    for u, v, R in pipes:
        nodes.add(u); nodes.add(v)
    unknown = sorted(n for n in nodes if n not in pressures)   # вузли без заданого тиску
    idx = {n: i for i, n in enumerate(unknown)}
    m = len(unknown)

    G = [[0.0] * m for _ in range(m)]        # матриця провідностей
    b = [0.0] * m                            # права частина
    for u, v, R in pipes:
        g = 1.0 / R
        for a, c in ((u, v), (v, u)):        # труба симетрична: внесок з обох боків
            if a in idx:
                i = idx[a]
                G[i][i] += g                 # діагональ: сума провідностей вузла
                if c in idx:
                    G[i][idx[c]] -= g        # позадіагональ: −провідність зв'язку
                else:
                    b[i] += g * pressures[c]  # сусід із заданим тиском → у праву частину

    p_unknown = solve_linear(G, b)
    p = dict(pressures)
    for n, i in idx.items():
        p[n] = p_unknown[i]

    # витрати по трубах: Q = (p_u − p_v)/R, додатна — від u до v
    Q = {(u, v): (p[u] - p[v]) / R for u, v, R in pipes}
    return p, Q
