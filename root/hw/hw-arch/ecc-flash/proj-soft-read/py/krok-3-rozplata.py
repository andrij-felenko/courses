def simulate(rber, N, M):
    sigma = sigma_for_rber(rber)
    edges = REF + RETRY * sigma
    table = band_llr_table(edges, sigma)

    msg   = rng.integers(0, 2, M)                       # M збережених бітів
    means = np.where(msg == 0, MU0, MU1)[:, None]
    vth   = means + sigma * rng.standard_normal((M, N)) # M×N аналогових порогів

    rber_emp = np.mean((vth > REF).astype(int) != msg[:, None])

    hard_dec  = ((vth > REF).sum(axis=1) > N/2).astype(int)          # більшість голосів
    full_dec  = (llr_full(vth, sigma).sum(axis=1) < 0).astype(int)   # сума певностей
    quant_dec = (table[np.digitize(vth, edges)].sum(axis=1) < 0).astype(int)

    wer = lambda dec: np.mean(dec != msg)
    hard_an = sum(comb(N, k) * rber**k * (1-rber)**(N-k) for k in range(N//2+1, N+1))
    soft_an = Q(sqrt(N) * q_inv(rber))
    return sigma, rber_emp, edges, table, wer(hard_dec), wer(quant_dec), wer(full_dec), hard_an, soft_an
