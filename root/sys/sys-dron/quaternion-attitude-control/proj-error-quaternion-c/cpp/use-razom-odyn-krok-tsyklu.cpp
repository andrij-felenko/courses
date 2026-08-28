// повний крок керування орієнтацією: вхід — виміри, вихід — команди моторів
void attitude_control_step(quat q_meas, quat q_des, const float omega[3],
                           float thrust_base, float motor[N_MOTORS]) {
    // 0. гігієна: виміряна орієнтація має бути одиничною
    quat_normalize(&q_meas);

    // 1. похибка як доворот + короткий шлях
    quat e = quat_error(q_des, q_meas);
    quat_shortest(&e);

    // 2. PD-момент по трьох осях тіла
    static const float Kp = 4.0f, Kd = 0.5f;
    float tau[3];
    tau[0] = -Kp * e.x - Kd * omega[0];
    tau[1] = -Kp * e.y - Kd * omega[1];
    tau[2] = -Kp * e.z - Kd * omega[2];

    // 3. розкидання моменту на актуатори (зашита матриця розподілу)
    allocate(tau, thrust_base, motor);

    // 4. затиснути в межі, зберігши напрямок моменту
    saturate_preserve(motor);
}
