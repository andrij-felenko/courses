def egcd(a: int, b: int):
    """Повертає (g, x, y): a·x + b·y = g = НСД(a, b)."""
    old_r, r = a, b
    old_x, x = 1, 0
    old_y, y = 0, 1
    while r:                              # звичайний Евклід…
        q = old_r // r
        old_r, r = r, old_r - q * r
        old_x, x = x, old_x - q * x       # …і ті самі кроки над коефіцієнтами
        old_y, y = y, old_y - q * y
    return old_r, old_x, old_y

def inverse(a: int, m: int) -> int:
    """a⁻¹ mod m. Існує тільки за НСД(a, m) = 1."""
    g, x, _ = egcd(a, m)
    if g != 1:
        raise ValueError(f"оберненого немає: НСД({a}, {m}) = {g}")
    return x % m                          # ← ця остача не косметична, див. нижче

assert egcd(3, 40) == (1, -13, 1)         # 3·(−13) + 40·1 = 1
assert inverse(3, 40) == 27               # d із рахунку на папері
