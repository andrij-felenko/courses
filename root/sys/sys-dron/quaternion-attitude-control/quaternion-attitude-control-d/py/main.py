# кватерніон — четвірка (w, x, y, z)

def quat_error(qd, qm):
    """q_err = q_d ⊗ q_meas⁻¹  (обидва одиничні)"""
    qi = (qm[0], -qm[1], -qm[2], -qm[3])   # обернений = спряжений
    aw, ax, ay, az = qd
    bw, bx, by, bz = qi
    return (
        aw*bw - ax*bx - ay*by - az*bz,
        aw*bx + ax*bw + ay*bz - az*by,
        aw*by - ax*bz + ay*bw + az*bx,
        aw*bz + ax*by - ay*bx + az*bw,
    )

def attitude_torque(qd, qm, w, Kp, Kd):
    """момент по трьох осях: PD за векторною частиною + демпфування по ω"""
    ew, ex, ey, ez = quat_error(qd, qm)
    if ew < 0.0:           # короткий шлях: не крутити «навколо світу»
        ex, ey, ez = -ex, -ey, -ez
    return (
        -Kp*ex - Kd*w[0],
        -Kp*ey - Kd*w[1],
        -Kp*ez - Kd*w[2],
    )
