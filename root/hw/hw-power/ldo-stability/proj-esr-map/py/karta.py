GOOD, EDGE = 45.0, 30.0     # пороги запасу фази: спокійно / на межі


def esr_map(loop, c_lo, c_hi, rows, esr_lo, esr_hi, cols):
    """Площина (Cвих, ESR) у символах: # запас ≥45°, + ≥30°, . менше."""
    def grid(lo, hi, n):
        step = (math.log10(hi) - math.log10(lo)) / (n - 1)
        return [10.0 ** (math.log10(lo) + i * step) for i in range(n)]

    esrs = grid(esr_lo, esr_hi, cols)
    out = []
    for cout in reversed(grid(c_lo, c_hi, rows)):
        line = ""
        for esr in esrs:
            _, pm = loop.margin(cout, esr)
            line += "#" if pm >= GOOD else ("+" if pm >= EDGE else ".")
        out.append("%7.1f |%s|" % (cout * 1e6, line))
    return out


def wall(loop, cout, target, lo, hi):
    """ESR, на якому запас фази дорівнює target, у вилці [lo, hi]. None —
    якщо на кінцях вилки запас по один бік порога: стіни тут просто нема."""
    def excess(esr):
        _, pm = loop.margin(cout, esr)
        return (pm if pm is not None else -999.0) - target
    if excess(lo) * excess(hi) > 0:
        return None
    for _ in range(60):
        mid = math.sqrt(lo * hi)
        if excess(lo) * excess(mid) <= 0:
            hi = mid
        else:
            lo = mid
    return math.sqrt(lo * hi)
