Q10 = 2.0   # множник Арреніуса на +10 °C (консервативно)

# Поправка SoC на саморозряд за час сну (лінійна модель).
# k_ref — паспортний темп, %/місяць за t_ref_C (напр. 2.0 за 25 °C).
def self_discharge_loss(k_ref, t_ref_C, t_cell_C, sleep_months):
    k = k_ref * Q10 ** ((t_cell_C - t_ref_C) / 10.0)   # темп при T
    return k * sleep_months                            # втрата, %

# на пробудженні:
soc_percent -= self_discharge_loss(2.0, 25.0, temp_C, months_asleep)
soc_percent = max(soc_percent, 0.0)
