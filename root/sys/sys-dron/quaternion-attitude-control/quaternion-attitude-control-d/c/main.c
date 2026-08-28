typedef struct { float w, x, y, z; } quat;

// q_err = q_d ⊗ q_meas⁻¹  (обидва одиничні)
quat quat_error(quat qd, quat qm) {
    quat qi = { qm.w, -qm.x, -qm.y, -qm.z };   // обернений = спряжений
    quat e;
    e.w = qd.w*qi.w - qd.x*qi.x - qd.y*qi.y - qd.z*qi.z;
    e.x = qd.w*qi.x + qd.x*qi.w + qd.y*qi.z - qd.z*qi.y;
    e.y = qd.w*qi.y - qd.x*qi.z + qd.y*qi.w + qd.z*qi.x;
    e.z = qd.w*qi.z + qd.x*qi.y - qd.y*qi.x + qd.z*qi.w;
    return e;
}

// момент по трьох осях: PD за векторною частиною + демпфування по ω
void attitude_torque(quat qd, quat qm, const float w[3],
                     float Kp, float Kd, float tau[3]) {
    quat e = quat_error(qd, qm);
    if (e.w < 0.0f) {           // короткий шлях: не крутити «навколо світу»
        e.x = -e.x; e.y = -e.y; e.z = -e.z;
    }
    tau[0] = -Kp*e.x - Kd*w[0];
    tau[1] = -Kp*e.y - Kd*w[1];
    tau[2] = -Kp*e.z - Kd*w[2];
}
