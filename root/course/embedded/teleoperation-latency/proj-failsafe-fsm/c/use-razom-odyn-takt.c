extern void apply_operator_cmd(void);   // звичайне телекерування (NORMAL)
extern void hold_last_cmd(void);        // тримати останню команду (HOLD)
extern float drive_get_speed(void);     // поточна швидкість, м/с
extern void  drive_set_speed(float v);  // задати швидкість приводу

void fs_init(failsafe_t *fs, uint32_t now_ms)
{
    fs->state          = FS_NORMAL;
    fs->last_change_ms = now_ms;
    fs->beacon         = false;
    beacon_set(false);
}

// Викликати щотакту головного циклу приводу.
// dt_s — тривалість такту (с); hb_period_ms — оцінений період серцебиття.
void fs_update(failsafe_t *fs, uint32_t now_ms, float dt_s,
               uint32_t uplink_silent_ms, uint32_t downlink_silent_ms,
               uint32_t hb_period_ms)
{
    uint32_t silent = fs_worst_silence(uplink_silent_ms, downlink_silent_ms);
    fs_state_t next = fs_target_state(silent, hb_period_ms);

    // --- Побічні дії ПЕРЕХОДУ (лише коли стан справді змінюється) ---
    if (next != fs->state) {
        fs_log_transition(fs->state, next, now_ms);   // «чорна скринька»
        fs->last_change_ms = now_ms;

        bool want_beacon = (next == FS_SAFE_STOP || next == FS_RTL);
        if (want_beacon != fs->beacon) {
            fs->beacon = want_beacon;
            beacon_set(want_beacon);                  // маяк увімк/вимк
        }
        if (next == FS_RTL)
            fs_enter_policy();                        // Hold / RTL / SmartRTL — ОДИН раз

        fs->state = next;
    }

    // --- Поведінка ПОТОЧНОГО стану (щотакту) ---
    switch (fs->state) {
        case FS_NORMAL:
            apply_operator_cmd();                     // слухаємо оператора
            break;
        case FS_HOLD:
            hold_last_cmd();                          // не смикаємо кермо
            break;
        case FS_SAFE_STOP:
            drive_set_speed(ramp_to_stop(drive_get_speed(), dt_s));  // плавно в нуль
            break;
        case FS_RTL:
            // Приводом керує вже логіка місії (RTL/SmartRTL веде маршрут),
            // або, якщо політика Hold, машина просто стоїть після рампи.
            break;
    }
}
