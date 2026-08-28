def anf_eval(coef, x):                # значення полінома на наборі x
    acc, m = 0, x
    while True:
        acc ^= coef[m]                # ⊕ коефіцієнти всіх підмножин x
        if m == 0:
            break
        m = (m - 1) & x               # наступна підмножина маски x
    return acc

def anf_degree(coef):                 # алгебричний степінь = найдовший живий доданок
    return max((m.bit_count() for m, c in enumerate(coef) if c), default=-1)

def is_affine(coef):                  # лінійна (афінна) ⟺ степінь ≤ 1
    return all(c == 0 or m.bit_count() < 2 for m, c in enumerate(coef))
