#include <array>

// Таблиця передпольотних умов. Додати нову перевірку — дописати рядок.
static constexpr std::array PREARM_CHECKS = {
    check_compass,
    check_gps,
    check_battery,
    check_ekf_converged,   // оцінка стану збіглася?
    check_rc_link,         // канал керування живий?
    // ... решта перевірок апарата
};

// Прогнати всі; повернути ПЕРШУ причину відмови (або nullptr, якщо все гаразд).
const char *prearm_first_failure() {
    for (auto check : PREARM_CHECKS) {
        PrearmResult r = check();
        if (!r.pass) {
            gcs_send_text("PreArm: %s", r.reason);   // назвати причину оператору
            return r.reason;
        }
    }
    return nullptr;   // усі припущення підтверджені
}
