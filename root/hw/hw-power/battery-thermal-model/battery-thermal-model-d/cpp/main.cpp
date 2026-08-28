// Аварійне відсічення пакета за температурою.
// Виклик — з періодичного таска BMS (напр. 10 разів на секунду).
constexpr float T_WARN_C   = 45.0f;   // попередження: підрізати струм
constexpr float T_CUTOFF_C = 60.0f;   // відсічення: розімкнути силовий ключ

void battery_thermal_guard(float t_pack_c)
{
    if (t_pack_c >= T_CUTOFF_C) {
        pack_fet_open();          // розімкнути навантаження — приплив тепла в нуль
        fault_latch(FAULT_OVERTEMP);
    } else if (t_pack_c >= T_WARN_C) {
        charge_current_limit(0);  // припинити заряд
        discharge_derate();       // урізати дозволений струм розряду
    }
}
