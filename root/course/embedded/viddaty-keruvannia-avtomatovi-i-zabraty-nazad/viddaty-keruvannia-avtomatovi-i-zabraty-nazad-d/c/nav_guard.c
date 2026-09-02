#include "nav_guard.h"

#include <math.h>

#define NAV_TRACK_LIMIT_DEG 30.0f /* наскільки можна довернути курс від лінії */
#define NAV_ROLL_LIMIT_DEG  25.0f
#define NAV_PITCH_UP_DEG    10.0f
#define NAV_PITCH_DOWN_DEG  (-8.0f)
#define RAD2DEG             57.2957795f

void nav_guard_init(nav_guard_t *g, const nav_setpoint_t *sp) {
    if (!g || !sp) return;
    g->sp = *sp;
    g->kp_xte = 0.9f;
    g->ki_xte = 0.6f;
    g->kd_xte = 0.4f;
    g->i_max = 30.0f;
    g->decay_tau = 0.4f;
    g->k_track = 1.5f;
    g->kp_alt = 0.6f;
    g->kp_spd = 0.03f;
    g->thr_trim = 0.62f;
    g->integral = 0.0f;
    g->prev_xte = 0.0f;
    g->have_prev = false;
    g->anti_windup = true;
}

float nav_guard_bearing(const nav_guard_t *g) {
    if (!g) return 0.0f;
    return atan2f(g->sp.wp_y - g->sp.leg_y, g->sp.wp_x - g->sp.leg_x) * RAD2DEG;
}

float nav_guard_crosstrack(const nav_guard_t *g, const vehicle_state_t *st) {
    if (!g || !st) return 0.0f;
    float dx = g->sp.wp_x - g->sp.leg_x;
    float dy = g->sp.wp_y - g->sp.leg_y;
    const float len = sqrtf(dx * dx + dy * dy);
    if (len < 1e-3f) return 0.0f; /* вироджений відрізок — відхиляти нема від чого */
    dx /= len;
    dy /= len;
    /* Векторний добуток: додатне значення — апарат ліворуч від лінії. */
    return dx * (st->y - g->sp.leg_y) - dy * (st->x - g->sp.leg_x);
}

control_command_t nav_guard_step(nav_guard_t *g,
                                 const vehicle_state_t *st,
                                 bool frozen,
                                 float dt_sec) {
    control_command_t u = { 0.0f, 0.0f, 0.0f, 0.0f };
    if (!g || !st) return u;

    const float dt = clampf(dt_sec, 0.0002f, 0.1f);
    const bool freeze = frozen && g->anti_windup;

    float xte = nav_guard_crosstrack(g, st);
    float d_xte = g->have_prev ? (xte - g->prev_xte) / dt : 0.0f;
    g->prev_xte = xte;
    g->have_prev = true;

    if (freeze) {
        /* Керує пілот. Інтегрування зупинено, накопичене згасає за τ, а лінія
           шляху перекладається так, щоб проходити через поточну точку: коли
           автомат отримає керування назад, його похибка дорівнюватиме нулю. */
        g->integral *= expf(-dt / g->decay_tau);
        g->sp.leg_x = st->x;
        g->sp.leg_y = st->y;
        g->sp.alt_target = st->alt;
        xte = 0.0f;
        d_xte = 0.0f;
        g->prev_xte = 0.0f;
    } else {
        g->integral += g->ki_xte * xte * dt;
        g->integral = clampf(g->integral, -g->i_max, g->i_max);
    }

    /* Інтеграл тут має фізичний сенс кута зносу: на бічному вітрі він
       сходиться до кута крабування, потрібного, щоб триматися лінії. */
    const float corr = clampf(g->kp_xte * xte + g->integral + g->kd_xte * d_xte,
                              -NAV_TRACK_LIMIT_DEG, NAV_TRACK_LIMIT_DEG);
    const float heading_demand = nav_guard_bearing(g) - corr;

    u.roll = clampf(g->k_track * wrap180(st->heading_deg - heading_demand),
                    -NAV_ROLL_LIMIT_DEG, NAV_ROLL_LIMIT_DEG);
    u.pitch = clampf(g->kp_alt * (g->sp.alt_target - st->alt),
                     NAV_PITCH_DOWN_DEG, NAV_PITCH_UP_DEG);
    u.yaw = 0.0f; /* розворот координований креном, окремої команди рискання нема */
    u.throttle = clampf(g->thr_trim + g->kp_spd * (g->sp.airspeed_target - st->airspeed),
                        0.0f, 1.0f);
    return u;
}
