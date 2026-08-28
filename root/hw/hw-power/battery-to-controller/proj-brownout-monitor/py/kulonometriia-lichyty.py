# Груба кулонометрія: накопичуємо витрачений заряд у мікроампер-секундах,
# щоб не втрачати точність на малих струмах, і переводимо в мА·год за запитом.

spent_uas = 0                    # витрачено, мкА·с (мікроампер-секунди)
BATTERY_CAPACITY_MAH = 2000      # паспортна ємність комірки

# Викликається періодично (напр., раз на секунду) з поточним струмом у мкА.
def coulomb_tick(current_ua, dt_ms):
    global spent_uas
    # ΔQ [мкА·с] = струм [мкА] × час [с] = current_ua × dt_ms / 1000
    spent_uas += current_ua * dt_ms // 1000

# Скільки мА·год лишилось (0, якщо перебрали).
def coulomb_remaining_mah():
    # 1 мА·год = 1000 мкА × 3600 с = 3 600 000 мкА·с
    spent_mah = spent_uas // 3600000
    if spent_mah >= BATTERY_CAPACITY_MAH:
        return 0
    return BATTERY_CAPACITY_MAH - spent_mah
