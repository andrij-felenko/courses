# Таблиця передпольотних умов. Додати нову перевірку — дописати рядок.
PREARM_CHECKS = (
    check_compass,
    check_gps,
    check_battery,
    check_ekf_converged,   # оцінка стану збіглася?
    check_rc_link,         # канал керування живий?
    # ... решта перевірок апарата
)

# Прогнати всі; повернути ПЕРШУ причину відмови (або None, якщо все гаразд).
def prearm_first_failure() -> str | None:
    for check in PREARM_CHECKS:
        r = check()
        if not r.passed:
            gcs_send_text(f"PreArm: {r.reason}")   # назвати причину оператору
            return r.reason
    return None   # усі припущення підтверджені
