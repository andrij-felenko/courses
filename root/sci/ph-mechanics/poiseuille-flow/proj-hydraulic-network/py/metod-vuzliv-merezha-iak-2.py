def solve_linear(A, b):
    """Розв'язати A·x = b (щільна невелика система) методом Гаусса
    з вибором головного елемента за стовпцем. A — рядки, b — вектор."""
    n = len(b)
    M = [row[:] + [b[i]] for i, row in enumerate(A)]   # робоча копія з правою частиною
    for col in range(n):
        piv = max(range(col, n), key=lambda r: abs(M[r][col]))   # головний елемент
        if abs(M[piv][col]) < 1e-300:
            raise ValueError("вироджена система: немає єдиного розв'язку")
        M[col], M[piv] = M[piv], M[col]
        for r in range(col + 1, n):          # прямий хід: занулюємо стовпець нижче
            f = M[r][col] / M[col][col]
            for c in range(col, n + 1):
                M[r][c] -= f * M[col][c]
    x = [0.0] * n
    for i in range(n - 1, -1, -1):           # зворотний хід
        s = M[i][n] - sum(M[i][c] * x[c] for c in range(i + 1, n))
        x[i] = s / M[i][i]
    return x
