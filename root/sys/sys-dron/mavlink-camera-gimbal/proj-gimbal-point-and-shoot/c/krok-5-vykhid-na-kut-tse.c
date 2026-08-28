/* Тангаж і рискання з кватерніона (послідовність ZYX). */
static void q_to_pitch_yaw(const float q[4], float *pitch, float *yaw)
{
    const float w = q[0], x = q[1], y = q[2], z = q[3];
    float s = 2.0f * (w * y - z * x);
    if (s >  1.0f) s =  1.0f;
    if (s < -1.0f) s = -1.0f;
    *pitch = asinf(s);
    *yaw   = atan2f(2.0f * (w * z + x * y), 1.0f - 2.0f * (y * y + z * z));
}

static bool wait_on_target(float want_pitch, float want_yaw, bool want_earth,
                           float tol, uint32_t timeout_ms)
{
    const uint32_t t0 = now_ms();
    mavlink_message_t m;

    while (now_ms() - t0 < timeout_ms) {
        if (!recv_msg(&m, 100)) continue;
        if (m.msgid != MAVLINK_MSG_ID_GIMBAL_DEVICE_ATTITUDE_STATUS) continue;

        mavlink_gimbal_device_attitude_status_t st;
        mavlink_msg_gimbal_device_attitude_status_decode(&m, &st);

        if (st.failure_flags & (GIMBAL_DEVICE_ERROR_FLAGS_AT_YAW_LIMIT |
                                GIMBAL_DEVICE_ERROR_FLAGS_AT_PITCH_LIMIT))
            return false;                   /* уперся: далі чекати нема сенсу */

        float pitch, yaw;
        q_to_pitch_yaw(st.q, &pitch, &yaw);

        /* Рамку звіту задають прапорці пристрою, а не твоє бажання. */
        const bool in_earth = st.flags & GIMBAL_DEVICE_FLAGS_YAW_IN_EARTH_FRAME;
        const bool in_body  = st.flags & GIMBAL_DEVICE_FLAGS_YAW_IN_VEHICLE_FRAME;
        if (!in_earth && !in_body) continue;          /* рамка не оголошена — не гадаємо */
        if (in_earth != want_earth) {
            if (!isfinite(st.delta_yaw)) continue;    /* нема чим перевести          */
            yaw = wrap_pi(want_earth ? yaw + st.delta_yaw : yaw - st.delta_yaw);
        }

        if (fabsf(wrap_pi(yaw - want_yaw)) < tol && fabsf(pitch - want_pitch) < tol)
            return true;
    }
    return false;
}
