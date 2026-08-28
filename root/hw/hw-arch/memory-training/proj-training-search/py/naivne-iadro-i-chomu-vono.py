# НАЇВНО, НЕ ВЖИВАТИ: перша й остання одиниця, середина між ними.
def center_naive(pf_map: list[bool]) -> int:
    n = len(pf_map)
    lo = 0
    while lo < n and not pf_map[lo]:      # перша P
        lo += 1
    hi = n - 1
    while hi >= 0 and not pf_map[hi]:     # остання P
        hi -= 1
    return (lo + hi) // 2                 # «центр»
