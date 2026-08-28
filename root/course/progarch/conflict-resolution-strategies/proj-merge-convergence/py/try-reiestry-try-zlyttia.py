# ── 2. Двійники: набір версій, кожна з версійним вектором ──
def dominates(x, y):                 # x строго новіший за y?
    keys = set(x) | set(y)
    ge = all(x.get(k, 0) >= y.get(k, 0) for k in keys)
    gt = any(x.get(k, 0) >  y.get(k, 0) for k in keys)
    return ge and gt

def sib_merge(a, b):
    both = a + b
    live, seen = [], set()
    for v in both:
        k = tuple(sorted(v["vv"].items()))
        if k in seen:                                     # дубль тієї самої версії
            continue
        if any(dominates(w["vv"], v["vv"]) for w in both):  # хтось новіший — відкинути
            continue
        seen.add(k); live.append(v)
    return live
