from math import comb, log

def p_fail(n: int, k: int, p: float) -> float:
    """Залишкова ймовірність загибелі блока (n, k) за частки втрат p:
    хвіст біномного розподілу P(L > n - k)."""
    e, q = n - k, 1.0 - p
    survive = sum(comb(n, j) * p**j * q**(n - j) for j in range(e + 1))
    return 1.0 - survive

def choose_block(p: float, rate: float, target: float, n_max: int) -> tuple | None:
    """Найкоротший блок швидкості ~rate, що дає ризик ≤ target.
    Повертає (n, k, e, ризик) або None, якщо в межу n_max не влізли."""
    if rate >= 1 - p:                       # над ємністю — марно за будь-якого n
        raise ValueError(f"R={rate} ≥ ємність 1−p={1-p}: ціль недосяжна")
    for n in range(2, n_max + 1):
        k = round(rate * n)
        if 0 < k < n and p_fail(n, k, p) <= target:
            return n, k, n - k, p_fail(n, k, p)
    return None

print(choose_block(p=0.05, rate=0.8, target=1e-3, n_max=200))
# → (23, 18, 5, 0.0007540…)   ← найкоротший блок під ціль 0.1 %
