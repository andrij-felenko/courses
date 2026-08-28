def two_squares(p):
    """Для простого p ≡ 1 (mod 4) повертає (x, y) з x² + y² = p.
    Спуск на множнику: тримаємо x² + y² = p·m і женемо m до 1."""
    # іскра: a² ≡ −1 (mod p) — беремо найменший такий лишок
    a = next(a for a in range(1, p) if (a * a + 1) % p == 0)
    x, y, m = a, 1, (a * a + 1) // p
    while m > 1:
        # залишки x, y за модулем m, зведені в межі (−m/2, m/2]
        u = x % m
        v = y % m
        if u > m // 2: u -= m
        if v > m // 2: v -= m
        # тотожність + ділення на m²: нова пара квадратів, менший множник
        nx = (x * u + y * v) // m
        ny = (x * v - y * u) // m
        x, y, m = abs(nx), abs(ny), (u * u + v * v) // m
    assert x * x + y * y == p
    return x, y
