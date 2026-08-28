def scan(q, n_max, t_max=5):
    """Пари (n,t), де арифметика бодай ДОЗВОЛЯЄ досконалий код:
    V мусить ділити q^n націло, інакше M = q^n/V не ціле — і коду нема."""
    tried, hits = 0, []
    for n in range(1, n_max + 1):
        qn = q ** n                     # рахуємо раз на n, не на кожне t
        for t in range(1, t_max + 1):
            if 2 * t + 1 > n:           # d = 2t+1 не буває довшою за слово
                continue
            tried += 1
            V = ball(n, t, q)
            if qn % V == 0:
                hits.append((n, t, qn // V))
    return tried, hits
