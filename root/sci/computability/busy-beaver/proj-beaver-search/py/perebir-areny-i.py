from itertools import product

def hunt(n, cap):
    A = 4 * n + 4                           # дій на клітинку
    cells = 2 * n
    ranges = [[7]] + [range(A)] * (cells - 1)   # A,0 = 7 = (1,R,B) фіксовано
    total = halted = undecided = 0
    best_ones = best_steps = 0
    for combo in product(*ranges):          # усі таблиці арени
        table = list(combo)
        total += 1
        ok, steps, ones = simulate(table, n, cap)
        if ok:
            halted += 1
            best_ones = max(best_ones, ones)     # рекорд одиниць → Σ(n)
            best_steps = max(best_steps, steps)  # рекорд кроків  → S(n)
        else:
            undecided += 1                       # ще працює на стелі
    return total, halted, undecided, best_ones, best_steps
