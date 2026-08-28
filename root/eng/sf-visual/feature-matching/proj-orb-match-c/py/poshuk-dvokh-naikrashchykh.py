# індекс найкращого дескриптора в B для заданого query;
# повертає (best_j, best, second) — дві найменші відстані Гаммінга.
def orb_two_best(query: int, B: list[int]) -> tuple[int, int, int]:
    best, second, best_j = 257, 257, -1          # 257 > будь-якої реальної відстані
    for j, desc in enumerate(B):
        d = orb_hamming(query, desc)
        if d < best:                             # новий рекорд: старий best з'їжджає в second
            second = best
            best = d
            best_j = j
        elif d < second:                         # не рекорд, але кращий за другий
            second = d
    return best_j, best, second                  # best_j = -1, лише якщо B порожній
