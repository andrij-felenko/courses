def nonneg(a, b, c):
    kind, data = solve(a, b, c)
    if kind != "family":
        return kind, []                          # "none" або "all"
    x1, y1, sx, sy, g = data
    lo = hi = None                               # межі на t: lo ≤ t ≤ hi
    for coef, base in ((sx, x1), (sy, y1)):
        if coef == 0:                            # координата зафіксована
            if base < 0:
                return "none", []                # …і вона від'ємна — розв'язків немає
            continue
        if coef > 0:                             # t ≥ ⌈−base/coef⌉
            v = -(base // coef)
            lo = v if lo is None else max(lo, v)
        else:                                    # t ≤ ⌊base/(−coef)⌋
            v = base // -coef
            hi = v if hi is None else min(hi, v)
    if lo is None or hi is None:                 # вікно відкрите з одного боку
        return "infinite", []
    return "list", [(x1 + sx * t, y1 + sy * t) for t in range(lo, hi + 1)]
