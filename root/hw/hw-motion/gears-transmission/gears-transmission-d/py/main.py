# Чи потягне привід задане навантаження через редуктор?
# motor_torque, load_torque — Н·м;  ratio — передавальне число (>1 = сповільнення);
# eff — ККД редуктора (0..1, напр. 0.9)
def drive_can_pull(motor_torque, ratio, eff, load_torque):
    out_torque = motor_torque * ratio * eff   # реальний момент на виході
    return out_torque >= load_torque          # з урахуванням втрат


# приклад виклику: мотор 0.02 Н·м, редуктор 1:40, ККД 0.9, навантаження 0.6 Н·м
# drive_can_pull(0.02, 40.0, 0.9, 0.6) -> True  (0.72 >= 0.6)
