# Пороги: за трохи до апаратних меж — щоб діяти РАНІШЕ за тротлінг плати.
TEMP_WARN_C = 75.0    # °C: гаряче, час притишити задачу
TEMP_CRIT_C = 82.0    # °C: критично, скинути важке навантаження
VOLT_MIN_MV = 4750    # мВ: нижче — шина просіла, недовольтаж близько

def read_soc_temp_c():
    """Читання температури кристала (Linux: millidegrees у thermal_zone0)."""
    try:
        with open("/sys/class/thermal/thermal_zone0/temp") as f:
            return int(f.read()) / 1000.0    # 61000 → 61.0 °C
    except (OSError, ValueError):
        return None                          # не змогли прочитати — віддаємо «нема даних»

def power_thermal_guard(temp_c, rail_mv):
    """Реакція на стан живлення й тепла. Повертає рівень тривоги 0..2."""
    alarm = 0

    if rail_mv > 0 and rail_mv < VOLT_MIN_MV:
        print(f"УВАГА: шина {rail_mv} мВ — просадка, недовольтаж близько")
        alarm = 2                            # просадка живлення — одразу важкий рівень

    if temp_c >= TEMP_CRIT_C:
        print(f"КРИТИЧНО: кристал {temp_c:.1f}°C — скидаю важке навантаження")
        alarm = max(alarm, 2)
    elif temp_c >= TEMP_WARN_C:
        print(f"гаряче: кристал {temp_c:.1f}°C — притишую задачу")
        alarm = max(alarm, 1)
    return alarm                             # 0 норма · 1 притишити · 2 скинути навантаження
