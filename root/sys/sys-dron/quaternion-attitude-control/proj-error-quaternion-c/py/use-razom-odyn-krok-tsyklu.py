# повний крок керування орієнтацією: вхід — виміри, вихід — команди моторів
def attitude_control_step(q_meas: Quat, q_des: Quat, omega, thrust_base: float):
    # 0. гігієна: виміряна орієнтація має бути одиничною
    quat_normalize(q_meas)

    # 1. похибка як доворот + короткий шлях
    e = quat_error(q_des, q_meas)
    quat_shortest(e)

    # 2. PD-момент по трьох осях тіла
    Kp, Kd = 4.0, 0.5
    tau = [
        -Kp * e.x - Kd * omega[0],
        -Kp * e.y - Kd * omega[1],
        -Kp * e.z - Kd * omega[2],
    ]

    # 3. розкидання моменту на актуатори (зашита матриця розподілу)
    motor = allocate(tau, thrust_base)

    # 4. затиснути в межі, зберігши напрямок моменту
    saturate_preserve(motor)
    return motor
