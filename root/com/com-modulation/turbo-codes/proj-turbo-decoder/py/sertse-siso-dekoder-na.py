NEG = -1e30

def siso(Ls, Lp, La):
    N = len(Ls)

    def gamma(k, s, u):                 # логарифм гілкової метрики + куди веде
        ns, p = TRELLIS[s][u]
        us = 1.0 if u else -1.0
        ps = 1.0 if p else -1.0
        return 0.5 * (us * (La[k] + Ls[k]) + ps * Lp[k]), ns

    # ── уперед: alpha[k][s] — логарифм імовірності дійти до стану s у час k ──
    alpha = [[NEG]*NS for _ in range(N+1)]
    alpha[0][0] = 0.0                   # старт відомий: стан 0
    for k in range(N):
        for s in range(NS):
            if alpha[k][s] <= NEG: continue
            for u in (0, 1):
                g, ns = gamma(k, s, u)
                alpha[k+1][ns] = maxstar(alpha[k+1][ns], alpha[k][s] + g)
        mx = max(alpha[k+1])            # нормуємо — інакше числа попливуть
        for s in range(NS):
            if alpha[k+1][s] > NEG: alpha[k+1][s] -= mx

    # ── назад: beta[k][s] — логарифм імовірності з s дотягти до кінця ──
    beta = [[NEG]*NS for _ in range(N+1)]
    for s in range(NS): beta[N][s] = 0.0   # кінець невідомий → всі стани рівно
    for k in range(N-1, -1, -1):
        for s in range(NS):
            for u in (0, 1):
                g, ns = gamma(k, s, u)
                beta[k][s] = maxstar(beta[k][s], beta[k+1][ns] + g)
        mx = max(beta[k])
        for s in range(NS):
            if beta[k][s] > NEG: beta[k][s] -= mx

    # ── повний LLR і зовнішня частка ──
    Le = [0.0]*N
    for k in range(N):
        num = den = NEG                 # логсуми гілок з u=1 / u=0
        for s in range(NS):
            if alpha[k][s] <= NEG: continue
            for u in (0, 1):
                g, ns = gamma(k, s, u)
                v = alpha[k][s] + g + beta[k+1][ns]
                if u: num = maxstar(num, v)
                else: den = maxstar(den, v)
        Le[k] = (num - den) - Ls[k] - La[k]   # прибрати канал і апріорі
    return Le
