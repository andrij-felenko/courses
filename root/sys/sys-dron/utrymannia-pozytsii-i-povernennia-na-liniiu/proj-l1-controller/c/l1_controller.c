/* l1_controller.c - Реалізація алгоритму наведення L1 на C */
#include "l1_controller.h"

static float l1_clamp(float val, float min_v, float max_v) {
    if (val < min_v) return min_v;
    if (val > max_v) return max_v;
    return val;
}

void l1_init(l1_state_t* ctrl, float period_l1, float roll_limit_deg) {
    ctrl->params.period_l1 = period_l1;
    ctrl->params.damping_ratio = 0.70710678f;
    ctrl->params.k_i = 0.035f;
    ctrl->params.i_limit = 25.0f;
    ctrl->params.roll_limit_rad = roll_limit_deg * (L1_PI / 180.0f);
    ctrl->params.min_l1_dist = 15.0f;
    ctrl->params.max_l1_dist = 250.0f;

    ctrl->integrator_ect = 0.0f;
    ctrl->cross_track_err = 0.0f;
    ctrl->lookahead_dist = 20.0f;
    ctrl->accel_cmd = 0.0f;
    ctrl->roll_cmd = 0.0f;
}

void l1_reset_integrator(l1_state_t* ctrl) {
    ctrl->integrator_ect = 0.0f;
}

bool l1_update_line(l1_state_t* ctrl,
                    l1_vec2_t pos,
                    l1_vec2_t vel,
                    l1_vec2_t wa,
                    l1_vec2_t wb,
                    float dt) {
    const float speed = sqrtf(vel.x * vel.x + vel.y * vel.y);
    if (speed < 1.0f) {
        ctrl->accel_cmd = 0.0f;
        ctrl->roll_cmd = 0.0f;
        return false;
    }

    /* 1. Вектор лінії шляху AB */
    const float ab_x = wb.x - wa.x;
    const float ab_y = wb.y - wa.y;
    const float ab_len = sqrtf(ab_x * ab_x + ab_y * ab_y);
    if (ab_len < 1.0f) {
        return false;
    }
    const float u_ab_x = ab_x / ab_len;
    const float u_ab_y = ab_y / ab_len;

    /* 2. Позиція відносно точки WA */
    const float a_x = pos.x - wa.x;
    const float a_y = pos.y - wa.y;

    /* 3. Поздовжня проєкція та бічне відхилення d */
    const float along_track = a_x * u_ab_x + a_y * u_ab_y;
    /* Псевдоскалярний добуток a x u_ab: додатне значення - праворуч від шляху */
    const float cross_track = a_x * u_ab_y - a_y * u_ab_x;
    ctrl->cross_track_err = cross_track;

    /* 4. Адаптація L1 до поточної швидкості: L1 = (T_L1 * V) / (sqrt(2) * pi) */
    float l1 = (ctrl->params.period_l1 * speed) / (1.41421356f * L1_PI);
    l1 = l1_clamp(l1, ctrl->params.min_l1_dist, ctrl->params.max_l1_dist);
    ctrl->lookahead_dist = l1;

    /* 5. Оновлення інтегратора вітру з обмеженням anti-windup */
    if (fabsf(cross_track) < l1) {
        ctrl->integrator_ect += cross_track * ctrl->params.k_i * dt;
        ctrl->integrator_ect = l1_clamp(ctrl->integrator_ect,
                                        -ctrl->params.i_limit,
                                        ctrl->params.i_limit);
    }
    const float effective_ct = cross_track + ctrl->integrator_ect;

    /* 6. Пошук точки прицілювання p_ref на лінії шляху */
    float along_ref = along_track;
    if (fabsf(effective_ct) < l1) {
        const float dx_ref = sqrtf(l1 * l1 - effective_ct * effective_ct);
        along_ref = along_track + dx_ref;
    } else {
        /* При великому відхиленні проєктуємо вперед на фіксовану відстань */
        along_ref = along_track + 0.1f * l1;
    }

    const float ref_x = wa.x + along_ref * u_ab_x;
    const float ref_y = wa.y + along_ref * u_ab_y;

    /* 7. Вектор від апарата до точки прицілювання */
    const float l1_vec_x = ref_x - pos.x;
    const float l1_vec_y = ref_y - pos.y;
    const float l1_actual_dist = sqrtf(l1_vec_x * l1_vec_x + l1_vec_y * l1_vec_y);
    if (l1_actual_dist < 1.0f) {
        return false;
    }

    /* 8. Розрахунок sin(eta) через векторний добуток V x L1 */
    const float cross_v_l1 = (vel.x * l1_vec_y - vel.y * l1_vec_x) / (speed * l1_actual_dist);
    const float sin_eta = l1_clamp(cross_v_l1, -1.0f, 1.0f);

    /* 9. Розрахунок нормального прискорення a_s = 2 * (V^2 / L1) * sin(eta) */
    float accel = 2.0f * (speed * speed / l1) * sin_eta;

    /* 10. Обмеження за граничним кутом крену та перерахунок у roll_cmd */
    const float max_accel = L1_GRAVITY * tanf(ctrl->params.roll_limit_rad);
    accel = l1_clamp(accel, -max_accel, max_accel);

    ctrl->accel_cmd = accel;
    ctrl->roll_cmd = atan2f(accel, L1_GRAVITY);
    return true;
}

bool l1_update_orbit(l1_state_t* ctrl,
                     l1_vec2_t pos,
                     l1_vec2_t vel,
                     l1_vec2_t center,
                     float radius,
                     bool clockwise,
                     float dt) {
    const float speed = sqrtf(vel.x * vel.x + vel.y * vel.y);
    if (speed < 1.0f || radius < 5.0f) {
        return false;
    }

    /* Вектор від центру до апарата */
    const float d_cx = pos.x - center.x;
    const float d_cy = pos.y - center.y;
    const float dist_to_center = sqrtf(d_cx * d_cx + d_cy * d_cy);
    if (dist_to_center < 1.0f) {
        return false;
    }

    /* Бічне відхилення від орбіти */
    const float sign = clockwise ? 1.0f : -1.0f;
    const float cross_track = sign * (dist_to_center - radius);
    ctrl->cross_track_err = cross_track;

    float l1 = (ctrl->params.period_l1 * speed) / (1.41421356f * L1_PI);
    l1 = l1_clamp(l1, ctrl->params.min_l1_dist, ctrl->params.max_l1_dist);
    ctrl->lookahead_dist = l1;

    /* Доцентрове прискорення стаціонарної орбіти + корекція L1 */
    const float a_centripetal = sign * (speed * speed / radius);

    /* Кут випередження на колі */
    const float alpha = l1 / (2.0f * radius);
    const float sin_alpha = l1_clamp(alpha, -1.0f, 1.0f);

    float accel = a_centripetal - 2.0f * (speed * speed / l1) * sin_alpha * (cross_track / l1);
    const float max_accel = L1_GRAVITY * tanf(ctrl->params.roll_limit_rad);
    accel = l1_clamp(accel, -max_accel, max_accel);

    ctrl->accel_cmd = accel;
    ctrl->roll_cmd = atan2f(accel, L1_GRAVITY);
    return true;
}
