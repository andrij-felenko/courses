static float setpoint   = 21.0f;    // бажана температура, °C
static float hyst        = 0.5f;    // піврозмах мертвої зони Δ, °C
static bool  heater_on   = false;   // ПАМʼЯТЬ: поточний стан реле

static void apply_hysteresis(float t) {
    if (heater_on) {
        // Гріємо — вимкнемо ЛИШЕ коли перевалили верхній поріг set + Δ.
        if (t > setpoint + hyst) {
            heater_on = false;
            relay_set(false);
        }
    } else {
        // Не гріємо — увімкнемо ЛИШЕ коли впали під нижній поріг set − Δ.
        if (t < setpoint - hyst) {
            heater_on = true;
            relay_set(true);
        }
    }
}
