from math import comb, isqrt

def ball(n, t, q=2):
    """Скільки слів у кулі радіуса t навколо одного слова.
    Псуємо рівно i позицій із n — це comb(n, i) виборів позицій;
    у кожній зіпсованій позиції стоїть один із (q−1) чужих символів."""
    return sum(comb(n, i) * (q - 1) ** i for i in range(t + 1))


def packing_limit(n, t, q=2):
    """Межа Геммінга: більше за стільки кодових слів не буває."""
    return q ** n // ball(n, t, q)


def is_perfect(n, t, M, q=2):
    """Досконалий ⟺ M куль радіуса t заповнюють q^n слів БЕЗ залишку."""
    return M * ball(n, t, q) == q ** n
