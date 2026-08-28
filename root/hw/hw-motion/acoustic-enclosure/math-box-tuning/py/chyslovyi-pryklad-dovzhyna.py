import math

C_SOUND = 343.0    # швидкість звуку при 20 °C, м/с


def port_length_m(fb: float, v_litres: float, d_m: float) -> float:
    """Довжина круглого порту (метри) під настройку fb.

    v_litres — об'єм коробки; d_m — діаметр порту в метрах.
    """
    V = v_litres * 1e-3          # літри → м³
    r = d_m * 0.5
    A = math.pi * r * r          # площа перерізу, м²
    w = 2.0 * math.pi * fb       # кутова частота

    l_eff = C_SOUND * C_SOUND * A / (w * w * V)  # ефективна довжина
    l_end = 2.0 * 0.85 * r       # поправка: ~0.85·d, обидва кінці
    l_phys = l_eff - l_end       # стільки різати трубу
    return l_phys


fb, V, d = 35.0, 30.0, 0.05
L = port_length_m(fb, V, d)
print(f"Фізична довжина порту = {L * 100.0:.1f} см")
