#include "control.h"

#include <math.h>

#define SETPOINT_TIMEOUT_US 100000u  /* 100 мс без свіжої уставки — це відмова */
#define LAND_THRUST         0.35f    /* газ керованого зниження */
#define LAND_RAMP_PER_S     0.60f    /* як швидко тяга сповзає до нього */

#define KP_ATT      6.5f     /* рад/с цільової швидкості на рад похибки кута */
#define KP_ATT_YAW  (KP_ATT * 0.6f)
#define RATE_MAX_XY 4.0f     /* рад/с */
#define RATE_MAX_Z  2.0f

#define KP_RATE     0.15f
#define KI_RATE     0.25f
#define KD_RATE     0.0035f
#define I_MAX_RATE  0.30f
#define D_CUTOFF_HZ 60.0f    /* похідну без фільтра на гіроскопі вмикати не можна */

void control_init(Control *c)
{
    c->rate_integral = v3(0.0f, 0.0f, 0.0f);
    c->gyro_prev = v3(0.0f, 0.0f, 0.0f);
    c->d_filtered = v3(0.0f, 0.0f, 0.0f);
    c->last_good.stamp_us = 0;
    c->last_good.q_target = quat_identity();
    c->last_good.rate_ff = v3(0.0f, 0.0f, 0.0f);
    c->last_good.thrust = 0.0f;
    c->have_setpoint = false;
    c->thrust_cmd = 0.0f;
    c->fallback = true;
}

ControlOutput control_step(Control *c,
                           SetpointMailbox *mb,
                           ControlFeedback *fb,
                           Quat q_est,
                           Vec3 gyro_rad_s,
                           float dt,
                           uint64_t now_us)
{
    /* 1. Забираємо уставку. Розірване читання — не аварія: тримаємо попередню
          цілісну копію, її вік однаково перевірить сторож. */
    Setpoint fresh;
    if (sp_consume(mb, &fresh) && fresh.stamp_us >= c->last_good.stamp_us) {
        c->last_good = fresh;
        c->have_setpoint = true;
    }

    Setpoint sp = c->last_good;
    const bool stale = !c->have_setpoint ||
                       (now_us - sp.stamp_us) > SETPOINT_TIMEOUT_US;

    /* 2. Сторож застарівання. Задача навігації зависла або радіоканал зник —
          регулятор не питає дозволу ні в кого: горизонт і плавне зниження. */
    if (stale) {
        sp.q_target = quat_identity();
        sp.rate_ff = v3(0.0f, 0.0f, 0.0f);
        c->thrust_cmd -= LAND_RAMP_PER_S * dt;
        if (c->thrust_cmd < LAND_THRUST) {
            c->thrust_cmd = LAND_THRUST;
        }
    } else {
        c->thrust_cmd = sp.thrust;
    }
    c->fallback = stale;
    fb_set_bit(fb, FB_FALLBACK, stale);

    /* 3. Петля орієнтації: пропорційна, від векторної частини похибки. */
    const Quat q_err = quat_mul(quat_conj(q_est), sp.q_target);
    const float sign = (q_err.w >= 0.0f) ? 1.0f : -1.0f;  /* найкоротший поворот */

    Vec3 rate_target = v3(
        2.0f * sign * q_err.x * KP_ATT + sp.rate_ff.x,
        2.0f * sign * q_err.y * KP_ATT + sp.rate_ff.y,
        2.0f * sign * q_err.z * KP_ATT_YAW + sp.rate_ff.z);

    rate_target.x = clampf(rate_target.x, -RATE_MAX_XY, RATE_MAX_XY);
    rate_target.y = clampf(rate_target.y, -RATE_MAX_XY, RATE_MAX_XY);
    rate_target.z = clampf(rate_target.z, -RATE_MAX_Z, RATE_MAX_Z);

    /* 4. Петля кутових швидкостей: повний PID на 1 кГц. */
    const Vec3 rate_err = v3_sub(rate_target, gyro_rad_s);

    const bool saturated = fb_test(fb, FB_SATURATED);
    if (!saturated) {
        c->rate_integral = v3_add(c->rate_integral, v3_scale(rate_err, KI_RATE * dt));
        c->rate_integral = v3(clampf(c->rate_integral.x, -I_MAX_RATE, I_MAX_RATE),
                              clampf(c->rate_integral.y, -I_MAX_RATE, I_MAX_RATE),
                              clampf(c->rate_integral.z, -I_MAX_RATE, I_MAX_RATE));
    }

    /* Похідна береться від ВИМІРЮВАННЯ, не від похибки: сходинка уставки інакше
       дає нескінченний сплеск. Плюс фільтр першого порядку на 60 Гц — сирий шум
       гіроскопа в D-ланці розігріває мотори швидше, ніж керує ними. */
    Vec3 d_raw = v3(0.0f, 0.0f, 0.0f);
    if (dt > 1e-6f) {
        d_raw = v3_scale(v3_sub(c->gyro_prev, gyro_rad_s), 1.0f / dt);
    }
    const float rc = 1.0f / (2.0f * 3.14159265f * D_CUTOFF_HZ);
    const float alpha = dt / (dt + rc);
    c->d_filtered = v3_add(c->d_filtered,
                           v3_scale(v3_sub(d_raw, c->d_filtered), alpha));
    c->gyro_prev = gyro_rad_s;

    const Vec3 raw_torque = v3_add(v3_add(v3_scale(rate_err, KP_RATE), c->rate_integral),
                                   v3_scale(c->d_filtered, KD_RATE));

    ControlOutput out;
    out.torque = v3(clampf(raw_torque.x, -1.0f, 1.0f),
                    clampf(raw_torque.y, -1.0f, 1.0f),
                    clampf(raw_torque.z, -1.0f, 1.0f));
    out.thrust = clampf(c->thrust_cmd, 0.0f, 1.0f);
    out.fallback = c->fallback;
    return out;
}
