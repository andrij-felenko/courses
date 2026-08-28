def n0_for(c):
    """Найменший поріг, від якого 3n²+5n+7 ≤ c·n² тримається назавжди."""
    last_fail = 0
    for n in range(1, 100_000):
        if 3*n*n + 5*n + 7 > c * n*n:   # нерівність ще НЕ виконана
            last_fail = n
    return last_fail + 1

print(n0_for(15))   # → 1   (тримає з першого n)
print(n0_for(4))    # → 7   (спершу треба дорости)
