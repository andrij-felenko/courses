# Чи потягне мотор-редуктор задане навантаження на вихідному валу?
# motor_torque, load_torque — Н·м;  ratio — передавальне число (>1 = сповільнення);
# eff — ККД редуктора (0..1, напр. 0.9)
def gearmotor_can_pull(motor_torque, ratio, eff, load_torque):
    out_torque = motor_torque * ratio * eff   # реальний момент на вихідному валу
    return out_torque >= load_torque          # з урахуванням втрат у редукторі


# приклад: мотор 0.02 Н·м, мотор-редуктор «1:40», ККД 0.9, навантаження 0.6 Н·м
# gearmotor_can_pull(0.02, 40.0, 0.9, 0.6) -> True   (0.72 >= 0.6)
