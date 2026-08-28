def bec_polarize(eps, n):
    """Z-значення 2**n синтетичних каналів для BEC(eps). Точна рекурсія."""
    zs = [eps]
    for _ in range(n):
        zs = [f(z) for z in zs for f in (lambda z: z*z,          # кращий W⁺
                                         lambda z: 2*z - z*z)]   # гірший W⁻
    return zs

for n in (2, 6, 10, 14, 18):
    zs = bec_polarize(0.5, n)
    good = sum(z < 1e-3 for z in zs) / len(zs)   # частка «майже досконалих»
    print(f"N={2**n:7d}   частка Z<0.001: {good:.3f}")
