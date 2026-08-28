INF = float("inf")

def viterbi(recv):
    T = len(recv) // 2
    metric = [0] + [INF] * (NSTATE - 1)      # старт відомий — стан 00
    survivor = []                            # survivor[t][s′] = (попередник, вхід)
    for t in range(T):
        r = (recv[2 * t], recv[2 * t + 1])
        nm = [INF] * NSTATE                  # нові метрики
        nb = [None] * NSTATE                 # нові вказівники назад
        for s in range(NSTATE):
            if metric[s] == INF:             # у цей стан ще не дійшли
                continue
            for u in (0, 1):
                out, ns = TRELLIS[(s, u)]
                branch = (out[0] ^ r[0]) + (out[1] ^ r[1])   # ADD: відстань Геммінга
                cand = metric[s] + branch
                if cand < nm[ns]:                            # COMPARE + SELECT
                    nm[ns], nb[ns] = cand, (s, u)
        metric = nm
        survivor.append(nb)
    # простеження назад від стану з найменшою метрикою
    best = min(range(NSTATE), key=lambda s: metric[s])
    s, bits = best, []
    for nb in reversed(survivor):
        ps, u = nb[s]
        bits.append(u)
        s = ps
    bits.reverse()
    return bits, metric[best]
