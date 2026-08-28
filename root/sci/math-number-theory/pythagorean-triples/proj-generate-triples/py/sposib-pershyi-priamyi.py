from math import gcd, isqrt

def primitive_triples(limit):
    """Усі примітивні трійки з гіпотенузою c ≤ limit."""
    for m in range(2, isqrt(limit) + 1):
        for n in range(1, m):
            c = m * m + n * n
            if c > limit:
                break                       # більші n лише збільшать c
            if (m - n) % 2 == 1 and gcd(m, n) == 1:   # різна парність + взаємна простота
                a, b = m * m - n * n, 2 * m * n
                yield (min(a, b), max(a, b), c)
