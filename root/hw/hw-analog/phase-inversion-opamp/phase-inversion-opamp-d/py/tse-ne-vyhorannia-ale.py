# Чи безпечний синфазний рівень для ОП на одному живленні 0..5 В?
# Вікно з довідника: [v_cm_min .. v_cm_max]. Сигнал може мати викид.

V_CM_MIN = 0.0    # нижня межа синфазного вікна, В
V_CM_MAX = 3.5    # верхня межа: V+ − 1.5 В
MARGIN   = 0.20   # запас на дрейф/температуру, В

def cm_level_safe(v_signal_peak: float) -> bool:
    lo = V_CM_MIN + MARGIN    # 0.20 В
    hi = V_CM_MAX - MARGIN    # 3.30 В
    return lo <= v_signal_peak <= hi

# приклад: давач інколи викидає до 3.8 В
#   cm_level_safe(3.8) → 3.8 > 3.30 → False → переворот можливий!
