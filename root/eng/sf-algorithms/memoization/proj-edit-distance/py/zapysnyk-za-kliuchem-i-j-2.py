from functools import lru_cache

def edit_distance(a, b):
    @lru_cache(maxsize=None)                    # кеш «(i, j) → результат» під капотом
    def rec(i, j):
        if i == 0:
            return j
        if j == 0:
            return i
        if a[i - 1] == b[j - 1]:
            return rec(i - 1, j - 1)
        return 1 + min(rec(i - 1, j), rec(i, j - 1), rec(i - 1, j - 1))
    return rec(len(a), len(b))
