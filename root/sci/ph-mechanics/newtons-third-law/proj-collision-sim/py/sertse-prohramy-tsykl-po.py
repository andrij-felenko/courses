def pair_forces(x, k, d0):
    """Силу кожної ПАРИ лічимо раз; +s тілу i, −s тілу j."""
    n = len(x)
    F = [0.0] * n
    for i in range(n):
        for j in range(i + 1, n):          # кожна пара рівно раз: i < j
            dx = x[i] - x[j]
            r = abs(dx)
            if 0.0 < r < d0:               # тіла торкаються?
                s = (k * (d0 - r)) * (dx / r)   # сила НА i, уздовж лінії центрів
                F[i] += s                  # дія
                F[j] -= s                  # протидія: те саме s, протилежний знак
    return F
