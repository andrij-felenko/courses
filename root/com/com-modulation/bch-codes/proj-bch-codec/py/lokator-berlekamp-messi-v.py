def berlekamp_massey(S):
    sigma, B, L = [1], [1], 0
    for n in range(len(S)):
        delta = S[n]                     # похибка (discrepancy)
        for i in range(1, L + 1):
            if i < len(sigma):
                delta ^= gf_mul(sigma[i], S[n - i])
        if delta == 0:
            B = [0] + B                  # x·B
        else:
            old = list(sigma)
            shifted = [gf_mul(delta, c) for c in ([0] + B)]   # δ·x·B
            ns = [0] * max(len(sigma), len(shifted))
            for i, c in enumerate(sigma):  ns[i] ^= c
            for i, c in enumerate(shifted): ns[i] ^= c
            sigma = ns
            if 2 * L <= n:
                L = n + 1 - L
                B = [gf_mul(gf_inv(delta), c) for c in old]   # δ⁻¹·σ_старий
            else:
                B = [0] + B
    while len(sigma) > 1 and sigma[-1] == 0:
        sigma.pop()
    return sigma, L
