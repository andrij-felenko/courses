# Один такт ACS для 4 станів (жорстке рішення).
# pm — метрики зараз; повертає нові метрики й вказівники назад.
def acs_step(pm, r0, r1):
    nm = [INF] * NSTATE
    nb = [None] * NSTATE
    for s in range(NSTATE):
        if pm[s] == INF:
            continue
        for u in (0, 1):
            out, ns = TRELLIS[(s, u)]
            bm = (out[0] ^ r0) + (out[1] ^ r1)   # відстань Геммінга
            cand = pm[s] + bm                     # ADD
            if cand < nm[ns]:                     # COMPARE + SELECT
                nm[ns], nb[ns] = cand, (s << 1) | u
    return nm, nb
