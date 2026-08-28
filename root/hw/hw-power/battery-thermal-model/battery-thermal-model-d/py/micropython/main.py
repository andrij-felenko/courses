# Аварійне відсічення пакета за температурою.
# Виклик — з періодичного таска BMS (напр. 10 разів на секунду).
T_WARN_C = const(45)      # попередження: підрізати струм (°C)
T_CUTOFF_C = const(60)    # відсічення: розімкнути силовий ключ (°C)


def battery_thermal_guard(t_pack_c):
    if t_pack_c >= T_CUTOFF_C:
        pack_fet_open()            # розімкнути навантаження — приплив тепла в нуль
        fault_latch(FAULT_OVERTEMP)
    elif t_pack_c >= T_WARN_C:
        charge_current_limit(0)    # припинити заряд
        discharge_derate()         # урізати дозволений струм розряду
