# SLO 99.9% за 30 діб  →  бюджет помилок = 0.1% запитів.
BUDGET   = 0.001         # 1 − SLO
PERIOD_H = 30 * 24       # 720 годин

def burn_rate(err_rate: float) -> float:
    # у скільки разів швидше за «рівно вичерпати за період»
    return err_rate / BUDGET

def budget_burned(err_rate: float, window_h: float) -> float:
    # частка 30-денного бюджету, з'їдена за вікно
    return burn_rate(err_rate) * window_h / PERIOD_H

def page(err_1h: float, err_5m: float) -> bool:
    # пейдж лише коли ОБИДВА вікна згодні: і година, і 5 хв горять 14.4×
    long_fast  = burn_rate(err_1h) >= 14.4   # тривке?
    short_fast = burn_rate(err_5m) >= 14.4   # ще триває?
    return long_fast and short_fast
