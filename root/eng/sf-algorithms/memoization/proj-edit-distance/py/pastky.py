from functools import lru_cache

@lru_cache(maxsize=None)
def rec(a, b):                                  # ПАСТКА: ключ — самі рядки
    if not a:
        return len(b)
    if not b:
        return len(a)
    if a[0] == b[0]:
        return rec(a[1:], b[1:])
    return 1 + min(rec(a[1:], b), rec(a, b[1:]), rec(a[1:], b[1:]))
