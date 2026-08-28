def combine(x, ox, y, oy, n):
    """З двох основ (порядки ox, oy) зібрати одну порядку НСК(ox, oy)."""
    z, oz = 1, 1
    for p, k in factorize(lcm(ox, oy)):
        pe = p ** k
        base, ob = (x, ox) if ox % pe == 0 else (y, oy)
        z = z * pow(base, ob // pe, n) % n  # шматок порядку рівно p^k
        oz *= pe
    return z, oz

def max_order_witness(n):
    """Основа g, взаємно проста з n, чий порядок дорівнює точно λ(n)."""
    target, g, g_ord, a = carmichael_lambda(n), 1, 1, 1
    while g_ord != target:
        a += 1
        if gcd(a, n) != 1:
            continue
        g, g_ord = combine(g, g_ord, a, multiplicative_order(a, n), n)
    return g
