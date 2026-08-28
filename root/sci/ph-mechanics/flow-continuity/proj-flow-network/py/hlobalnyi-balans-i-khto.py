def mass_balance(supply):
    """Глобальний баланс: сума всіх подач. У справній мережі = 0
    (скільки влилося джерелами, стільки й забрали стоки)."""
    return sum(supply.values())

def node_residuals(branches, supply, flow):
    """Нев'язка балансу в КОЖНОМУ вузлі: (вихід − вхід) − подача. Скрізь має бути ≈ 0."""
    nodes = {n for e in branches for n in e} | set(supply)
    res = {n: 0.0 for n in nodes}
    for (u, v), q in flow.items():
        res[u] += q                        # виходить з u
        res[v] -= q                        # входить у v
    for n in nodes:
        res[n] -= supply.get(n, 0.0)
    return res
