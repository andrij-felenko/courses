def nominal(factors):
    return {f.name: f.nom for f in factors}

# ── 1) точкова оцінка: усе на номіналі ──
def point(factors):
    return peak_rps(nominal(factors))

# ── 2) інтервал: добуток додатних діапазонів монотонний → досить кінців ──
def interval(factors):
    lo = peak_rps({f.name: f.lo for f in factors})   # усі нижні кінці
    hi = peak_rps({f.name: f.hi for f in factors})   # усі верхні кінці
    return lo, hi
