"""
Повна програмна реалізація алгоритму Берлекампа над полем GF(2).
Многочлени упаковуються в цілі бітові маски.
"""

def deg(p: int) -> int:
    """Обчислення степеня многочлена (номер найстаршого одиничного біта)."""
    return p.bit_length() - 1 if p > 0 else -1

def poly_add(a: int, b: int) -> int:
    """Додавання многочленів над GF(2) через побітовий XOR."""
    return a ^ b

def poly_mod(a: int, b: int) -> int:
    """Ділення многочлена a на b з остачею над GF(2)."""
    deg_b = deg(b)
    if deg_b < 0:
        raise ZeroDivisionError("Ділення на нульовий многочлен")
    while True:
        shift = deg(a) - deg_b
        if shift < 0:
            break
        a ^= (b << shift)
    return a

def poly_gcd(a: int, b: int) -> int:
    """Алгоритм Евкліда для обчислення найбільшого спільного дільника над GF(2)."""
    while b > 0:
        a, b = b, poly_mod(a, b)
    return a

def poly_mul(a: int, b: int) -> int:
    """Множення многочленів над GF(2)."""
    res = 0
    while b > 0:
        if b & 1:
            res ^= a
        a <<= 1
        b >>= 1
    return res

def build_berlekamp_matrix(f: int, n: int) -> list[list[int]]:
    """Побудова матриці Q розміру n x n, де рядок i містить коефіцієнти x^(2*i) mod f(x)."""
    q_matrix = []
    rem = 1
    for i in range(n):
        row = [(rem >> j) & 1 for j in range(n)]
        q_matrix.append(row)
        # Рекурентний перехід до x^(2*(i+1)) = (rem * x^2) mod f(x)
        rem = poly_mod(rem << 2, f)
    return q_matrix

def null_space_gf2(q_mat: list[list[int]], n: int) -> list[int]:
    """Знаходження базису ядра матриці (Q + I)^T методом виключення Гаусса."""
    m = [[q_mat[j][i] ^ (1 if i == j else 0) for j in range(n)] for i in range(n)]

    pivots = {}
    row = 0
    for col in range(n):
        pivot_row = -1
        for r in range(row, n):
            if m[r][col] == 1:
                pivot_row = r
                break
        if pivot_row == -1:
            continue
        m[row], m[pivot_row] = m[pivot_row], m[row]
        for r in range(n):
            if r != row and m[r][col] == 1:
                for c in range(col, n):
                    m[r][c] ^= m[row][c]
        pivots[col] = row
        row += 1

    free_cols = [c for c in range(n) if c not in pivots]
    basis = []
    for free_c in free_cols:
        vec = [0] * n
        vec[free_c] = 1
        for lead_c, r in pivots.items():
            if m[r][free_c] == 1:
                vec[lead_c] = 1
        poly_val = sum(vec[i] << i for i in range(n))
        basis.append(poly_val)
    return basis

def berlekamp_factor(f: int) -> list[int]:
    """Повний рекурсивний розклад многочлена f(x) на незвідні множники."""
    n = deg(f)
    if n <= 1:
        return [f]

    q_mat = build_berlekamp_matrix(f, n)
    basis = null_space_gf2(q_mat, n)

    if len(basis) == 1:
        return [f]

    v = basis[1]
    g1 = poly_gcd(f, v)
    g2 = poly_gcd(f, v ^ 1)

    factors = []
    for g in [g1, g2]:
        if deg(g) > 0:
            factors.extend(berlekamp_factor(g))
    return factors
