def blahut_arimoto(Q, tol=1e-9, max_iter=10_000):
    """Ємність DMC із матрицею переходів Q[x, y] = P(y | x).
    Повертає (C у бітах, оптимальний вхідний розподіл, число ітерацій)."""
    Q = np.asarray(Q, float)
    r = np.full(Q.shape[0], 1.0 / Q.shape[0])       # старт: рівномірний вхід
    for step in range(1, max_iter + 1):
        q = r @ Q                                    # вихід q(y) = Σ_x r(x) Q(y|x)
        with np.errstate(divide="ignore", invalid="ignore"):
            logterm = np.where(Q > 0, np.log2(Q / q), 0.0)   # 0·log0 → 0
        D = (Q * logterm).sum(axis=1)                # D_x = KL(Q(·|x) ‖ q), біт
        lower = float(r @ D)                         # Σ r(x)·D_x  ≤ C
        upper = float(D.max())                       # max_x D_x   ≥ C
        if upper - lower < tol:                      # розрив менший за поріг — стоп
            return lower, r, step
        r = r * np.exp2(D)                           # r(x) ← r(x)·2^{D_x}
        r /= r.sum()                                 # перенормувати у розподіл
    return lower, r, max_iter
