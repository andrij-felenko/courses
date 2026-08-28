def gauss(A, b):
    """Розв'язати A·x = b (щільна невелика система) методом Гаусса з півотингом."""
    n = len(A)
    M = [A[i][:] + [b[i]] for i in range(n)]          # робоча копія з правою частиною
    for c in range(n):
        piv = max(range(c, n), key=lambda r: abs(M[r][c]))   # головний елемент стовпця
        if abs(M[piv][c]) < 1e-300:
            raise ValueError("вироджена система балансів — розв'язок не єдиний")
        M[c], M[piv] = M[piv], M[c]
        for r in range(n):
            if r != c and M[r][c]:
                f = M[r][c] / M[c][c]
                for k in range(c, n + 1):
                    M[r][k] -= f * M[c][k]
        # рядок c лишається з провідним M[c][c]; ділення — в кінці
    return [M[i][n] / M[i][i] for i in range(n)]
