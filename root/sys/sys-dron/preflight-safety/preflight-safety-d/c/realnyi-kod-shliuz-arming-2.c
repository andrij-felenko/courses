// Таблиця передпольотних умов. Додати нову перевірку — дописати рядок.
static prearm_result_t (*const PREARM_CHECKS[])(void) = {
    check_compass,
    check_gps,
    check_battery,
    check_ekf_converged,   // оцінка стану збіглася?
    check_rc_link,         // канал керування живий?
    // ... решта перевірок апарата
};
#define NUM_CHECKS (sizeof(PREARM_CHECKS) / sizeof(PREARM_CHECKS[0]))

// Прогнати всі; повернути ПЕРШУ причину відмови (або NULL, якщо все гаразд).
const char *prearm_first_failure(void) {
    for (size_t i = 0; i < NUM_CHECKS; i++) {
        prearm_result_t r = PREARM_CHECKS[i]();
        if (!r.pass) {
            gcs_send_text("PreArm: %s", r.reason);   // назвати причину оператору
            return r.reason;
        }
    }
    return NULL;   // усі припущення підтверджені
}
