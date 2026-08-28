def ev_low(p, x):                 # оцінка; молодший степінь — перший
    y, xp = 0, 1
    for c in p:
        y ^= mul(c, xp)
        xp = mul(xp, x)
    return y

def rs_syndromes(r, nsym):
    """Sⱼ = r(αʲ). Чисте слово ділиться на g → усі синдроми нульові."""
    return [p_eval(r, pw(2, j)) for j in range(nsym)]

def berlekamp_massey(S, nsym):
    """Найкоротший регістр, що породжує синдроми, — це локатор Λ(x)."""
    C, B = [1], [1]
    L, m, b = 0, 1, 1
    for n in range(nsym):
        d = S[n]
        for i in range(1, L + 1):
            d ^= mul(C[i], S[n - i])
        if d == 0:
            m += 1
            continue
        coef = div(d, b)
        if len(C) < len(B) + m:
            C = C + [0] * (len(B) + m - len(C))
        T_ = list(C)
        for i in range(len(B)):
            C[i + m] ^= mul(coef, B[i])
        if 2 * L <= n:
            L, B, b, m = n + 1 - L, T_, d, 1
        else:
            m += 1
    return C[:L + 1], L

def chien(lam, n):
    """Перебираємо позиції: де Λ(Xᵢ⁻¹) = 0, там помилка."""
    return [p for p in range(n) if ev_low(lam, inv(pw(2, n - 1 - p))) == 0]

def forney(S, lam, pos, n, nsym):
    """Yᵢ = Xᵢ · Ω(Xᵢ⁻¹) / Λ′(Xᵢ⁻¹), де Ω = S·Λ mod x^nsym."""
    omega = [0] * nsym
    for i, s in enumerate(S):
        if s:
            for j, l in enumerate(lam):
                if l and i + j < nsym:
                    omega[i + j] ^= mul(s, l)
    # формальна похідна: над GF(2ᵐ) виживають лише непарні степені
    lam_d = [(lam[k + 1] if (k + 1) % 2 else 0) for k in range(len(lam) - 1)]
    e = [0] * n
    for p in pos:
        X = pw(2, n - 1 - p)
        den = ev_low(lam_d, inv(X))
        if den == 0:
            return None
        e[p] = div(mul(X, ev_low(omega, inv(X))), den)
    return e

def rs_decode(r, nsym):
    """(слово, к-сть виправлень) або (None, −1) — чесна відмова."""
    S = rs_syndromes(r, nsym)
    if max(S) == 0:
        return list(r), 0
    lam, L = berlekamp_massey(S, nsym)
    if 2 * L > nsym:
        return None, -1
    pos = chien(lam, len(r))
    if len(pos) != L:
        return None, -1
    e = forney(S, lam, pos, len(r), nsym)
    if e is None:
        return None, -1
    out = [a ^ b for a, b in zip(r, e)]
    if max(rs_syndromes(out, nsym)) != 0:
        return None, -1
    return out, L
