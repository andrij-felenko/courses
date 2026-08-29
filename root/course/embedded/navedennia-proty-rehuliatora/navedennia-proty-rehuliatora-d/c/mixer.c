#include "mixer.h"

/* Стовпці: внесок tx, ty, tz у кожен мотор. Тяга додається всім однаково. */
static const float MIX[MOTOR_COUNT][3] = {
    { -1.0f, +1.0f, +1.0f },   /* 0: передній правий */
    { +1.0f, -1.0f, +1.0f },   /* 1: задній лівий */
    { +1.0f, +1.0f, -1.0f },   /* 2: передній лівий */
    { -1.0f, -1.0f, -1.0f },   /* 3: задній правий */
};

MixerOutput mixer_quad_x(Vec3 torque, float thrust)
{
    MixerOutput out;
    out.saturated = false;

    float mix[MOTOR_COUNT];
    float mix_min = 0.0f, mix_max = 0.0f;

    for (int i = 0; i < MOTOR_COUNT; ++i) {
        mix[i] = MIX[i][0] * torque.x + MIX[i][1] * torque.y + MIX[i][2] * torque.z;
        if (i == 0 || mix[i] < mix_min) mix_min = mix[i];
        if (i == 0 || mix[i] > mix_max) mix_max = mix[i];
    }

    /* Розмах моментів ширший за весь діапазон ШІМ — момент не вміщується взагалі.
       Ріжемо його пропорційно: краще менший, але неспотворений момент. */
    const float span = mix_max - mix_min;
    if (span > 1.0f) {
        const float gain = 1.0f / span;
        for (int i = 0; i < MOTOR_COUNT; ++i) {
            mix[i] *= gain;
        }
        mix_min *= gain;
        mix_max *= gain;
        out.saturated = true;
    }

    /* Тепер зсуваємо колективний газ так, щоб момент дійшов до рами цілим.
       Момент важливіший за тягу: втрата висоти — це метри, втрата моменту — падіння. */
    const float thrust_lo = -mix_min;
    const float thrust_hi = 1.0f - mix_max;
    const float thrust_adj = clampf(thrust, thrust_lo, thrust_hi);
    if (thrust_adj != thrust) {
        out.saturated = true;
    }

    for (int i = 0; i < MOTOR_COUNT; ++i) {
        out.motor[i] = clampf(thrust_adj + mix[i], MOTOR_IDLE, 1.0f);
    }
    return out;
}

void mixer_to_wrench(const float motor[MOTOR_COUNT], Vec3 *torque_out, float *thrust_out)
{
    float tx = 0.0f, ty = 0.0f, tz = 0.0f, t = 0.0f;
    for (int i = 0; i < MOTOR_COUNT; ++i) {
        tx += MIX[i][0] * motor[i];
        ty += MIX[i][1] * motor[i];
        tz += MIX[i][2] * motor[i];
        t  += motor[i];
    }
    *torque_out = v3(tx * 0.25f, ty * 0.25f, tz * 0.25f);
    *thrust_out = t * 0.25f;
}
