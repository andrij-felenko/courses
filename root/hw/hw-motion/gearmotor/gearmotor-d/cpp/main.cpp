#include <stdbool.h>

// Чи потягне мотор-редуктор задане навантаження на вихідному валу?
// motor_torque, load_torque — Н·м;  ratio — передавальне число (>1 = сповільнення);
// eff — ККД редуктора (0..1, напр. 0.9)
bool gearmotor_can_pull(float motor_torque, float ratio, float eff, float load_torque) {
    float out_torque = motor_torque * ratio * eff;   // реальний момент на вихідному валу
    return out_torque >= load_torque;                // з урахуванням втрат у редукторі
}

// приклад: мотор 0.02 Н·м, мотор-редуктор «1:40», ККД 0.9, навантаження 0.6 Н·м
// gearmotor_can_pull(0.02f, 40.0f, 0.9f, 0.6f) -> true   (0.72 >= 0.6)
