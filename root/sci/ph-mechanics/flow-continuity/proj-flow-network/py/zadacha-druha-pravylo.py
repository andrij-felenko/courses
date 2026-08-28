def solve_flow_network(branches, supply):
    """Гілкові витрати з самих балансів вузлів (правило вузла = Кірхгоф-I для потоку).
    branches: [(u, v), …] — гілка з опорним напрямом u→v (Q>0 означає течію з u в v).
    supply:   {вузол: q_зовн} — зовнішня подача: джерело > 0, стік < 0,
              проміжний вузол — 0 (можна не згадувати).
    Повертає {(u, v): Q} — витрату кожної гілки за її опорним напрямом."""
    nodes = sorted({n for e in branches for n in e} | set(supply))
    N, B = len(nodes), len(branches)

    if B < N - 1:
        raise ValueError(f"мережа незв'язна: гілок {B} < вузлів−1 = {N-1}")
    if B > N - 1:
        raise ValueError(f"у мережі є цикл (гілок {B} > вузлів−1 = {N-1}): "
                         "самої нерозривності мало — розподіл вирішує закон опору")

    ref = nodes[-1]                        # опорний вузол: його рівняння надлишкове
    rows = [n for n in nodes if n != ref]
    ri = {n: i for i, n in enumerate(rows)}

    A = [[0.0] * B for _ in rows]          # матриця інцидентності (без опорного рядка)
    b = [supply.get(n, 0.0) for n in rows]
    for j, (u, v) in enumerate(branches):
        if u in ri: A[ri[u]][j] += 1.0     # гілка ВИХОДИТЬ з u  →  +Q
        if v in ri: A[ri[v]][j] -= 1.0     # гілка ВХОДИТЬ у v   →  −Q

    q = gauss(A, b)
    return {branches[j]: q[j] for j in range(B)}
