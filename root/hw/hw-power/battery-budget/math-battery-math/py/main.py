# Усе в цілих: струми — мкА, час — секунди, ємність — мкА·год.
def avg_current_ua(i_sleep_ua: int, i_act_ua: int,
                   t_act_ms: int, period_ms: int) -> int:
    """Середній струм (мкА) для двостанового циклу сон/активність."""
    # I_avg = I_sleep + (I_act - I_sleep) * t_act / T
    extra = (i_act_ua - i_sleep_ua) * t_act_ms // period_ms
    return i_sleep_ua + extra


def life_hours(q_eff_uah: int, i_total_ua: int) -> int:
    """Прогноз життя в годинах від ЕФЕКТИВНОЇ ємності (мкА·год) і повного струму."""
    return q_eff_uah // i_total_ua if i_total_ua else 0


# Приклад використання:
#   iavg = avg_current_ua(12, 130000, 250, 60000)   # ≈ 554 мкА
#   qeff = 3000 * 1000 * 85 * 80 // 10000           # мкА·год
#   h    = life_hours(qeff, iavg + 3)  # + саморозряд ≈ 3 мкА → ≈ 3650 год
