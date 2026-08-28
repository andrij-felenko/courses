# Аварійне відсічення пакета за температурою.
# Виклик — з періодичного таска BMS (напр. 10 разів на секунду).
T_WARN_C = 45.0      # попередження: підрізати струм
T_CUTOFF_C = 60.0    # відсічення: розімкнути силовий ключ


def battery_thermal_guard(t_pack_c):
    if t_pack_c >= T_CUTOFF_C:
        pack_fet_open()            # розімкнути навантаження — приплив тепла в нуль
        fault_latch(FAULT_OVERTEMP)
    elif t_pack_c >= T_WARN_C:
        charge_current_limit(0)    # припинити заряд
        discharge_derate()         # урізати дозволений струм розряду
