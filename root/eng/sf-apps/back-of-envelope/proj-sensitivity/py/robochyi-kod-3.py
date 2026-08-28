# ── 3) Монте-Карло: тягнемо кожен множник із трикутного розподілу ──
def draw(f, rng):
    if f.lo == f.hi:                          # відоме точно → без розкиду
        return f.nom
    return rng.triangular(f.lo, f.hi, f.nom)  # (low, high, mode)

def monte_carlo(factors, n=100_000, seed=0):
    rng = random.Random(seed)                 # фіксований seed → відтворювано
    out = [peak_rps({f.name: draw(f, rng) for f in factors}) for _ in range(n)]
    out.sort()
    return out

def pct(sorted_out, p):                       # p-й перцентиль із відсортованого
    return sorted_out[min(len(sorted_out) - 1, int(p / 100 * len(sorted_out)))]

def frac_over(sorted_out, thr):               # частка прогонів, що перейшли поріг
    return 1.0 - bisect.bisect_right(sorted_out, thr) / len(sorted_out)
