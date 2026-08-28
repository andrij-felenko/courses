def icbrt(x: int) -> int:
    """Кубічний корінь у цілих — двійковим пошуком, без float."""
    lo, hi = 0, 1 << ((x.bit_length() + 2) // 3)
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if mid ** 3 <= x:
            lo = mid
        else:
            hi = mid - 1
    return lo

n = keygen(512)[0][0]
c = powmod(42, 3, n)
assert c == 42 ** 3                    # остачі не сталося взагалі
assert icbrt(c) == 42                  # m відновлено без ключа
