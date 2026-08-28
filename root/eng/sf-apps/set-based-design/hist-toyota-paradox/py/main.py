from bisect import bisect_left, bisect_right

MOTORS = [round(0.1 * i, 1) for i in range(1, 201)]   # каталог моторів: 0.1 … 20.0 Н·м
GEARS  = [5 * i for i in range(1, 61)]                # каталог редукторів: 5 … 300
LO, HI = 120.0, 130.0                                 # треба на виході, Н·м
# рівняння схеми:  T_вих = T_мотора · n

def enumerate_pairs():
    """Точка за точкою: помацати КОЖНУ пару."""
    hits, touched = [], 0
    for t in MOTORS:
        for n in GEARS:
            touched += 1
            if LO <= t * n <= HI:
                hits.append((t, n))
    return hits, touched

def narrow():
    """Наборами: вимогу переносимо назад крізь рівняння й ріжемо каталог."""
    hits, touched = [], 0
    g_lo, g_hi = GEARS[0], GEARS[-1]
    for t in MOTORS:
        touched += 1
        need_lo, need_hi = LO / t, HI / t      # яке n узагалі рятує цей мотор
        if need_hi < g_lo or need_lo > g_hi:
            continue                            # жоден редуктор — мінус УВЕСЬ ряд за один хід
        i = bisect_left(GEARS, need_lo)         # вікно придатних редукторів —
        j = bisect_right(GEARS, need_hi)        # двійковим пошуком, не переглядом
        for n in GEARS[i:j]:                    # торкаємось лише вікна
            touched += 1
            if LO <= t * n <= HI:
                hits.append((t, n))
    return hits, touched

e_hits, e_touched = enumerate_pairs()
n_hits, n_touched = narrow()

assert sorted(e_hits) == sorted(n_hits)   # ТІ САМІ відповіді — жодної не загублено
print(len(e_hits), e_touched, n_touched)  # 84 придатні пари; 12000 дотиків проти 284
