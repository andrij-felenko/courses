Woc = 0.40          # дефіцит Eg−qVoc + втрати, В (перше наближення)
kT  = 0.02585       # kT/q за 300 K, В

def power(gaps, C=1.0):
    "Потужність стосу P = Jстос·ΣV, мВт/см². C — концентрація (× сонць)."
    J = subcells(gaps)
    Jstack = min(J) * C
    V = sum(max(g - Woc, 0.0) + kT*np.log(C) for g in sorted(gaps))
    return Jstack * V

def best_triple(objective, lo=0.5, hi=2.3, step=0.02):
    "Перебір трійок порогів під максимум objective(gaps)."
    grid = np.arange(lo, hi, step)
    best = (-1.0, None)
    for e1 in grid:                          # верхній поріг
        for e2 in grid[grid < e1 - 0.05]:    # середній < верхнього
            for e3 in grid[grid < e2 - 0.05]:  # нижній < середнього
                val = objective([e1, e2, e3])
                if val > best[0]:
                    best = (val, (round(e1,2), round(e2,2), round(e3,2)))
    return best
