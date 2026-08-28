def ext_gcd(a: int, b: int) -> tuple[int, int, int]:
    """Повертає (d, x, y): d = НСД(a, b), причому a·x + b·y = d."""
    r0, r1 = a, b
    x0, x1 = 1, 0          # коефіцієнти при a
    y0, y1 = 0, 1          # коефіцієнти при b
    while r1:
        q = r0 // r1
        r0, r1 = r1, r0 - q * r1
        x0, x1 = x1, x0 - q * x1
        y0, y1 = y1, y0 - q * y1
    return r0, x0, y0


def mod_inverse(a: int, m: int) -> int:
    """Обернене до a за модулем m; помилка, якщо оберненого не існує."""
    d, x, _ = ext_gcd(a % m, m)
    if d != 1:
        raise ValueError(f"НСД({a}, {m}) = {d} ≠ 1 — оберненого не існує")
    return x % m            # x буває від'ємним — зводимо в [0, m)


# ext_gcd(1071, 462)  → (21, -3, 7)
# mod_inverse(17, 43) → 38
# Python рахує в довгій арифметиці, тож той самий код бере ключі RSA як є.
