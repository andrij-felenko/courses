import numpy as np

# Розв'язати A·x = b методом Гаусса з вибором ведучого. Повертає None,
# якщо матриця вироджена (кандидат геть плаский — не мітка).
def solve_linear(A, b):
    A = A.astype(np.float64).copy()
    b = b.astype(np.float64).copy()
    n = len(b)
    for col in range(n):
        # вибір ведучого рядка (найбільший за модулем елемент у стовпці) — стійкість
        piv = col + int(np.argmax(np.abs(A[col:, col])))
        if abs(A[piv, col]) < 1e-9:
            return None                          # вироджена → відкинути кандидата
        if piv != col:                           # переставити рядки piv ↔ col
            A[[col, piv]] = A[[piv, col]]
            b[[col, piv]] = b[[piv, col]]
        d = A[col, col]
        for r in range(n):                       # виключити стовпець з решти рядків
            if r == col:
                continue
            f = A[r, col] / d
            A[r, col:] -= f * A[col, col:]
            b[r] -= f * b[col]
    return b / np.diag(A)                         # діагональ → розв'язок

# Гомографія, що переводить 4 кути мітки src у квадрат [0..S]×[0..S].
# Повертає H як 3×3 (h8=1) або None. S — сторона канонічного квадрата в пікселях.
def homography_to_square(src, S):
    dst = [(0, 0), (S, 0), (S, S), (0, S)]
    A = np.zeros((8, 8))
    b = np.zeros(8)
    for i in range(4):
        xs, ys = src[i]
        X, Y = dst[i]
        A[2 * i]     = [xs, ys, 1, 0,  0,  0, -X * xs, -X * ys]
        A[2 * i + 1] = [0,  0,  0, xs, ys, 1, -Y * xs, -Y * ys]
        b[2 * i], b[2 * i + 1] = X, Y
    h = solve_linear(A, b)
    if h is None:
        return None
    return np.append(h, 1.0).reshape(3, 3)
