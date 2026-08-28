from itertools import product

def top_probability(phi, p):
    """Точна ймовірність вершини: зважена сума по ВСІХ 2ⁿ станах."""
    n = len(p)
    total = 0.0
    for x in product((0, 1), repeat=n):      # усі 2ⁿ наборів відмов
        if phi(x):                           # система впала на цьому наборі?
            w = 1.0
            for i in range(n):               # вага стану — добуток по листках
                w *= p[i] if x[i] else 1 - p[i]
            total += w
    return total

# система «2 з 3»: падає, коли відмовили хоча б два блоки
phi_2of3 = lambda x: sum(x) >= 2
print(top_probability(phi_2of3, [0.1, 0.1, 0.1]))   # ≈ 0.028
