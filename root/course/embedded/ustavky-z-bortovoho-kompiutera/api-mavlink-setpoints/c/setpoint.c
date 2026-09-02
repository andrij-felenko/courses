#include "setpoint.h"

#include <math.h>
#include <string.h>

static int finite3(float a, float b, float c)
{
    return isfinite(a) && isfinite(b) && isfinite(c);
}

static float clamp01(float v)
{
    if (v < 0.0f) return 0.0f;
    if (v > 1.0f) return 1.0f;
    return v;
}

/* Спільна частина кадру #84: адресат, система координат і маска. */
static void target_base(mavlink_set_position_target_local_ned_t *sp,
                        uint8_t target_sys, uint32_t boot_ms, uint16_t mask)
{
    memset(sp, 0, sizeof(*sp));
    /* boot_ms = 0 означає «застосувати негайно»: так робимо, поки годинники
       не зведені механізмом TIMESYNC. */
    sp->time_boot_ms = boot_ms;
    sp->target_system = target_sys;
    sp->target_component = MAV_COMP_ID_AUTOPILOT1;
    sp->coordinate_frame = MAV_FRAME_LOCAL_NED;
    sp->type_mask = mask;
}

int sp_position_ned(mavlink_message_t *out, uint8_t sys, uint8_t comp, uint8_t target_sys,
                    uint32_t boot_ms, float north_m, float east_m, float down_m, float yaw_rad)
{
    if (!finite3(north_m, east_m, down_m) || !isfinite(yaw_rad)) return -1;

    mavlink_set_position_target_local_ned_t sp;
    target_base(&sp, target_sys, boot_ms, PT_MASK_POSITION);
    /* Вісь Z дивиться вниз: п'ять метрів над точкою старту це down_m = -5. */
    sp.x = north_m;
    sp.y = east_m;
    sp.z = down_m;
    sp.yaw = yaw_rad;

    mavlink_msg_set_position_target_local_ned_encode(sys, comp, out, &sp);
    return 0;
}

int sp_velocity_ned(mavlink_message_t *out, uint8_t sys, uint8_t comp, uint8_t target_sys,
                    uint32_t boot_ms, float vn_ms, float ve_ms, float vd_ms, float yaw_rad)
{
    if (!finite3(vn_ms, ve_ms, vd_ms) || !isfinite(yaw_rad)) return -1;

    mavlink_set_position_target_local_ned_t sp;
    target_base(&sp, target_sys, boot_ms, PT_MASK_VELOCITY);
    sp.vx = vn_ms;
    sp.vy = ve_ms;
    sp.vz = vd_ms;      /* додатне — зниження */
    sp.yaw = yaw_rad;

    mavlink_msg_set_position_target_local_ned_encode(sys, comp, out, &sp);
    return 0;
}

int sp_velocity_yawrate(mavlink_message_t *out, uint8_t sys, uint8_t comp, uint8_t target_sys,
                        uint32_t boot_ms, float vn_ms, float ve_ms, float vd_ms, float yaw_rate_rads)
{
    if (!finite3(vn_ms, ve_ms, vd_ms) || !isfinite(yaw_rate_rads)) return -1;

    mavlink_set_position_target_local_ned_t sp;
    target_base(&sp, target_sys, boot_ms, PT_MASK_VELOCITY_YAWRATE);
    sp.vx = vn_ms;
    sp.vy = ve_ms;
    sp.vz = vd_ms;
    sp.yaw_rate = yaw_rate_rads;

    mavlink_msg_set_position_target_local_ned_encode(sys, comp, out, &sp);
    return 0;
}

int sp_position_ff_velocity(mavlink_message_t *out, uint8_t sys, uint8_t comp, uint8_t target_sys,
                            uint32_t boot_ms,
                            float north_m, float east_m, float down_m,
                            float vn_ms, float ve_ms, float vd_ms, float yaw_rad)
{
    if (!finite3(north_m, east_m, down_m) || !finite3(vn_ms, ve_ms, vd_ms) || !isfinite(yaw_rad))
        return -1;

    mavlink_set_position_target_local_ned_t sp;
    target_base(&sp, target_sys, boot_ms, PT_MASK_POSITION_FF_VELOCITY);
    /* Швидкість тут — випереджувальний член від генератора траєкторії.
       Якщо вона не узгоджена з різницею позицій, контури починають
       боротися між собою: саме той конфлікт, про який попереджає стаття. */
    sp.x = north_m;
    sp.y = east_m;
    sp.z = down_m;
    sp.vx = vn_ms;
    sp.vy = ve_ms;
    sp.vz = vd_ms;
    sp.yaw = yaw_rad;

    mavlink_msg_set_position_target_local_ned_encode(sys, comp, out, &sp);
    return 0;
}

int sp_attitude_thrust(mavlink_message_t *out, uint8_t sys, uint8_t comp, uint8_t target_sys,
                       uint32_t boot_ms, const float q[4], float thrust)
{
    if (!isfinite(q[0]) || !finite3(q[1], q[2], q[3]) || !isfinite(thrust)) return -1;

    const float n = sqrtf(q[0] * q[0] + q[1] * q[1] + q[2] * q[2] + q[3] * q[3]);
    if (!(n > 1e-6f)) return -1;    /* вироджений кватерніон надсилати не можна */

    mavlink_set_attitude_target_t at;
    memset(&at, 0, sizeof(at));
    at.time_boot_ms = boot_ms;
    at.target_system = target_sys;
    at.target_component = MAV_COMP_ID_AUTOPILOT1;
    at.type_mask = AT_MASK_ATTITUDE_THRUST;
    /* Норму зводимо до одиниці самі: відхилення понад 1% автопілот трактує
       як зіпсовану орієнтацію й лається CRITICAL_NAV_ATTITUDE_INVALID. */
    at.q[0] = q[0] / n;
    at.q[1] = q[1] / n;
    at.q[2] = q[2] / n;
    at.q[3] = q[3] / n;
    at.thrust = clamp01(thrust);

    mavlink_msg_set_attitude_target_encode(sys, comp, out, &at);
    return 0;
}

int sp_body_rates(mavlink_message_t *out, uint8_t sys, uint8_t comp, uint8_t target_sys,
                  uint32_t boot_ms, float roll_rate, float pitch_rate, float yaw_rate, float thrust)
{
    if (!finite3(roll_rate, pitch_rate, yaw_rate) || !isfinite(thrust)) return -1;

    mavlink_set_attitude_target_t at;
    memset(&at, 0, sizeof(at));
    at.time_boot_ms = boot_ms;
    at.target_system = target_sys;
    at.target_component = MAV_COMP_ID_AUTOPILOT1;
    at.type_mask = AT_MASK_RATES_THRUST;
    /* Кватерніон ігнорується маскою, але поле мусить лишатися валідним. */
    at.q[0] = 1.0f;
    at.body_roll_rate = roll_rate;
    at.body_pitch_rate = pitch_rate;
    at.body_yaw_rate = yaw_rate;
    at.thrust = clamp01(thrust);

    mavlink_msg_set_attitude_target_encode(sys, comp, out, &at);
    return 0;
}

void sp_quat_from_euler(float roll, float pitch, float yaw, float q_out[4])
{
    const float cr = cosf(roll * 0.5f), sr = sinf(roll * 0.5f);
    const float cp = cosf(pitch * 0.5f), sp = sinf(pitch * 0.5f);
    const float cy = cosf(yaw * 0.5f), sy = sinf(yaw * 0.5f);

    q_out[0] = cr * cp * cy + sr * sp * sy;   /* w */
    q_out[1] = sr * cp * cy - cr * sp * sy;   /* x */
    q_out[2] = cr * sp * cy + sr * cp * sy;   /* y */
    q_out[3] = cr * cp * sy - sr * sp * cy;   /* z */
}
