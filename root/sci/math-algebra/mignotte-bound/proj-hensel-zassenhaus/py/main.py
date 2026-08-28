import math
from typing import List, Tuple, Optional


def poly_deg(f: List[int]) -> int:
    """Повертає степінь многочлена (-1 для нульового многочлена)."""
    while len(f) > 1 and f[-1] == 0:
        f.pop()
    return len(f) - 1 if f and f != [0] else -1


def poly_norm_l2(f: List[int]) -> float:
    """Обчислює евклідову норму вектора коефіцієнтів ||f||_2."""
    return math.sqrt(sum(c * c for c in f))


def mignotte_bound(f: List[int]) -> int:
    """
    Обчислює межу Міньотта B(f) = C(n, n//2) * ||f||_2.
    Гарантує верхню оцінку на будь-який коефіцієнт будь-якого цілого дільника.
    """
    n = poly_deg(f)
    if n <= 1:
        return max(abs(c) for c in f) if f else 0
    k = n // 2
    comb = math.comb(n, k)
    l2 = poly_norm_l2(f)
    return int(math.ceil(comb * l2))


def poly_add_mod(a: List[int], b: List[int], p: int) -> List[int]:
    """Додавання многочленів за модулем p."""
    deg = max(len(a), len(b))
    res = [0] * deg
    for i in range(deg):
        c1 = a[i] if i < len(a) else 0
        c2 = b[i] if i < len(b) else 0
        res[i] = (c1 + c2) % p
    while len(res) > 1 and res[-1] == 0:
        res.pop()
    return res


def poly_sub_mod(a: List[int], b: List[int], p: int) -> List[int]:
    """Віднімання многочленів за модулем p."""
    deg = max(len(a), len(b))
    res = [0] * deg
    for i in range(deg):
        c1 = a[i] if i < len(a) else 0
        c2 = b[i] if i < len(b) else 0
        res[i] = (c1 - c2) % p
    while len(res) > 1 and res[-1] == 0:
        res.pop()
    return res


def poly_mul_mod(a: List[int], b: List[int], p: int) -> List[int]:
    """Множення многочленів за модулем p."""
    if not a or not b or a == [0] or b == [0]:
        return [0]
    res = [0] * (len(a) + len(b) - 1)
    for i, ca in enumerate(a):
        for j, cb in enumerate(b):
            res[i + j] = (res[i + j] + ca * cb) % p
    while len(res) > 1 and res[-1] == 0:
        res.pop()
    return res


def poly_divmod_p(a: List[int], b: List[int], p: int) -> Tuple[List[int], List[int]]:
    """Ділення многочленів з остачею в скінченному полі F_p[x]."""
    deg_a = poly_deg(a)
    deg_b = poly_deg(b)
    if deg_b < 0:
        raise ZeroDivisionError("Ділення на нульовий многочлен")
    if deg_a < deg_b:
        return [0], a[:]

    rem = a[:]
    quot = [0] * (deg_a - deg_b + 1)
    inv_lead_b = pow(b[-1], p - 2, p)

    for i in range(deg_a - deg_b, -1, -1):
        cur_deg = poly_deg(rem)
        if cur_deg == i + deg_b:
            coeff = (rem[-1] * inv_lead_b) % p
            quot[i] = coeff
            for j in range(deg_b + 1):
                rem[i + j] = (rem[i + j] - coeff * b[j]) % p
            while len(rem) > 1 and rem[-1] == 0:
                rem.pop()

    while len(quot) > 1 and quot[-1] == 0:
        quot.pop()
    return quot, rem


def poly_ext_gcd_p(a: List[int], b: List[int], p: int) -> Tuple[List[int], List[int], List[int]]:
    """
    Розширений алгоритм Евкліда для многочленів у F_p[x].
    Знаходить НСД та поліноми Безу s(x), t(x) такі, що s*a + t*b ≡ НСД (mod p).
    """
    if poly_deg(b) < 0:
        lead_inv = pow(a[-1], p - 2, p)
        gcd = [(c * lead_inv) % p for c in a]
        return gcd, [lead_inv], [0]

    q, r = poly_divmod_p(a, b, p)
    gcd, s1, t1 = poly_ext_gcd_p(b, r, p)
    s = t1
    t = poly_sub_mod(s1, poly_mul_mod(q, t1, p), p)
    return gcd, s, t


def hensel_step(f: List[int], g: List[int], h: List[int], s: List[int], t: List[int], m: int, p: int) -> Tuple[List[int], List[int], List[int], List[int]]:
    """
    Крок квадратичного підйому Гензеля:
    Піднімає f ≡ g * h (mod m) до (mod m * p) та оновлює розв'язки Безу.
    """
    m_next = m * p
    gh = poly_mul_mod(g, h, m_next)
    diff = [(f[i] if i < len(f) else 0) - (gh[i] if i < len(gh) else 0) for i in range(max(len(f), len(gh)))]
    e = [(c // m) % p for c in diff]

    se = poly_mul_mod(s, e, p)
    q, r = poly_divmod_p(se, h, p)

    te = poly_mul_mod(t, e, p)
    qg = poly_mul_mod(q, g, p)
    delta_g = poly_add_mod(te, qg, p)
    
    g_next = poly_add_mod(g, [c * m for c in delta_g], m_next)
    h_next = poly_add_mod(h, [c * m for c in r], m_next)

    # Підйом співвідношення Безу
    sg = poly_mul_mod(s, g_next, m_next)
    th = poly_mul_mod(t, h_next, m_next)
    one = [1]
    sum_st = poly_add_mod(sg, th, m_next)
    diff_b = [(sum_st[i] if i < len(sum_st) else 0) - (one[i] if i < len(one) else 0) for i in range(max(len(sum_st), len(one)))]
    b_poly = [(c // m) % p for c in diff_b]

    sb = poly_mul_mod(s, b_poly, p)
    q_b, r_b = poly_divmod_p(sb, h, p)

    tb = poly_mul_mod(t, b_poly, p)
    qg_b = poly_mul_mod(q_b, g, p)
    delta_s = poly_add_mod(tb, qg_b, p)

    s_next = poly_sub_mod(s, [c * m for c in delta_s], m_next)
    t_next = poly_sub_mod(t, [c * m for c in r_b], m_next)

    return g_next, h_next, s_next, t_next


def symmetric_mod(f: List[int], m: int) -> List[int]:
    """Симетричне відображення лишків з діапазону [0, m-1] у (-m/2, m/2]."""
    half = m // 2
    res = []
    for c in f:
        rem = c % m
        if rem > half:
            rem -= m
        res.append(rem)
    while len(res) > 1 and res[-1] == 0:
        res.pop()
    return res


def poly_div_exact_z(f: List[int], g: List[int]) -> Optional[List[int]]:
    """Точне ділення многочленів у кільці Z[x]."""
    deg_f = poly_deg(f)
    deg_g = poly_deg(g)
    if deg_g < 0:
        return None
    if deg_f < deg_g:
        return None if f != [0] else [0]

    rem = [float(c) for c in f]
    quot = [0] * (deg_f - deg_g + 1)
    lead_g = g[-1]

    for i in range(deg_f - deg_g, -1, -1):
        cur_deg = len(rem) - 1
        while cur_deg >= 0 and abs(rem[cur_deg]) < 1e-9:
            cur_deg -= 1
        if cur_deg == i + deg_g:
            val = rem[cur_deg] / lead_g
            if abs(val - round(val)) > 1e-5:
                return None
            coeff = int(round(val))
            quot[i] = coeff
            for j in range(deg_g + 1):
                rem[i + j] -= coeff * g[j]

    for c in rem:
        if abs(c) > 1e-5:
            return None
    while len(quot) > 1 and quot[-1] == 0:
        quot.pop()
    return quot


if __name__ == "__main__":
    # Тестовий поліном: f(x) = (x^3 + 2x - 3) * (x^3 - x^2 + 4)
    # f(x) = x^6 - x^5 + 2x^4 + x^3 - 8x^2 + 8x - 12
    f = [-12, 8, -8, 1, 2, -1, 1]
    
    bound = mignotte_bound(f)
    print(f"Вхідний многочлен f(x): {f}")
    print(f"Евклідова норма ||f||_2: {poly_norm_l2(f):.4f}")
    print(f"Межа Міньотта B(f): {bound}")

    p = 5
    target_modulus = 2 * bound
    print(f"Критерій зупинки підйому: p^k > {target_modulus}")

    # Модулярні дільники mod 5:
    g = [2, 2, 0, 1]
    h = [4, 0, 4, 1]

    gcd, s, t = poly_ext_gcd_p(g, h, p)
    print(f"Початкове співвідношення Безу: s={s}, t={t}")

    mod = p
    step = 1
    while mod <= target_modulus:
        g, h, s, t = hensel_step(f, g, h, s, t, mod, p)
        mod *= p
        print(f"Крок {step}: модуль = {mod}, g = {symmetric_mod(g, mod)}, h = {symmetric_mod(h, mod)}")
        step += 1

    g_final = symmetric_mod(g, mod)
    h_final = symmetric_mod(h, mod)
    print(f"\nВідновлені незвідні дільники в Z[x]:")
    print(f"g(x) = {g_final}")
    print(f"h(x) = {h_final}")

    quot = poly_div_exact_z(f, g_final)
    print(f"Перевірка точного ділення: {quot == h_final}")
