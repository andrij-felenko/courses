# Термінація NiMH за dT/dt: ловимо різкий нагрів у мить повноти.
DTDT_STOP_DC_PER_MIN = 10    # поріг 1.0 °C/хв, у десятих °C
SAMPLE_S             = 5     # період вимірювання температури, с

_t_prev_dc = 0              # попередня температура, десяті °C
_t_prev_ms = 0             # стан між викликами

def nimh_done(cell_temp_dc, now_ms):
    # cell_temp_dc — температура комірки в десятих градуса (напр., 253 = 25.3 °C)
    global _t_prev_dc, _t_prev_ms
    if _t_prev_ms == 0:             # перший виклик — лише запам'ятати
        _t_prev_dc = cell_temp_dc
        _t_prev_ms = now_ms
        return False
    if now_ms - _t_prev_ms < SAMPLE_S * 1000:
        return False                # ще рано міряти нахил

    d_temp = cell_temp_dc - _t_prev_dc          # приріст, десяті °C
    d_min  = (now_ms - _t_prev_ms) // 60000     # час, хвилини (цілі)
    _t_prev_dc = cell_temp_dc
    _t_prev_ms = now_ms

    # нахил у десятих °C за хвилину; ділення бережемо від нуля
    if d_min > 0 and d_temp // d_min >= DTDT_STOP_DC_PER_MIN:
        return True                 # комірка різко гріється → повна
    return False
