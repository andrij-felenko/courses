/* ============================================================================
 * scurve_planner.h & scurve_planner.c
 * Виробничий планувальник 7-сегментної S-кривої на мові C
 * ============================================================================ */
#include <math.h>
#include <stdbool.h>
#include <stdint.h>

typedef struct {
    double max_vel;   /* Максимальна швидкість (од/с)    */
    double max_acc;   /* Максимальне прискорення (од/с²) */
    double max_jerk;  /* Максимальний ривок (од/с³)      */
} scurve_limits_t;

typedef struct {
    double pos;       /* Поточне положення (од)          */
    double vel;       /* Поточна швидкість (од/с)        */
    double acc;       /* Поточне прискорення (од/с²)     */
} motion_state_t;

typedef struct {
    double t[7];      /* Тривалості сегментів T1..T7 (с) */
    double s_start[7];/* Початкові положення сегментів   */
    double v_start[7];/* Початкові швидкості сегментів   */
    double a_start[7];/* Початкові прискорення сегментів */
    double j_seg[7];  /* Ривок на кожному сегменті       */
    double t_total;   /* Повний час виконання профілю    */
    double start_pos; /* Початкова координата            */
    double target_pos;/* Цільова координата              */
    int dir;          /* Напрямок руху: +1 або -1        */
    bool planned;     /* Прапорець валідності профілю    */
} scurve_profile_t;

static inline double scurve_cbrt(double x) {
    return cbrt(x);
}

/* Ініціалізація та розрахунок профілю переміщення від s0 до s1 */
bool scurve_plan(scurve_profile_t *prof, const scurve_limits_t *lim,
                 double s0, double s1, double v0) {
    if (!prof || !lim || lim->max_vel <= 0.0 || lim->max_acc <= 0.0 || lim->max_jerk <= 0.0) {
        return false;
    }

    double dist = s1 - s0;
    prof->start_pos = s0;
    prof->target_pos = s1;

    if (fabs(dist) < 1e-9) {
        for (int i = 0; i < 7; ++i) prof->t[i] = 0.0;
        prof->t_total = 0.0;
        prof->dir = 1;
        prof->planned = true;
        return true;
    }

    prof->dir = (dist >= 0.0) ? 1 : -1;
    double S = fabs(dist);
    double v_max = lim->max_vel;
    double a_max = lim->max_acc;
    double j_max = lim->max_jerk;

    /* Час виходу на максимальне прискорення */
    double tj = a_max / j_max;
    double s_limit = 2.0 * (a_max * a_max * a_max) / (j_max * j_max);

    double tj1, tj2, ta, td, tv;
    double v_peak;

    if (S < s_limit) {
        /* Надкороткий рух: прискорення a_max не досягається */
        tj1 = scurve_cbrt(S / (2.0 * j_max));
        tj2 = tj1;
        ta = 0.0;
        td = 0.0;
        tv = 0.0;
    } else {
        /* Визначаємо досяжну швидкість */
        double a_sq_over_j = (a_max * a_max) / j_max;
        double discr = a_sq_over_j * a_sq_over_j + 4.0 * a_max * S;
        v_peak = (-a_sq_over_j + sqrt(discr)) * 0.5;

        if (v_peak < v_max) {
            /* Трикутний за швидкістю профіль (без фази cruise) */
            tj1 = tj;
            tj2 = tj;
            ta = (v_peak - a_sq_over_j) / a_max;
            td = ta;
            tv = 0.0;
        } else {
            /* Повний 7-сегментний рух */
            v_peak = v_max;
            tj1 = tj;
            tj2 = tj;
            ta = (v_max - a_sq_over_j) / a_max;
            td = ta;
            double s_acc = 0.5 * v_max * (2.0 * tj1 + ta);
            double s_dec = 0.5 * v_max * (2.0 * tj2 + td);
            tv = (S - (s_acc + s_dec)) / v_max;
            if (tv < 0.0) tv = 0.0;
        }
    }

    /* Заповнення масиву тривалостей фаз */
    prof->t[0] = tj1;
    prof->t[1] = ta;
    prof->t[2] = tj1;
    prof->t[3] = tv;
    prof->t[4] = tj2;
    prof->t[5] = td;
    prof->t[6] = tj2;

    /* Задання значень ривка для кожної фази */
    prof->j_seg[0] = +j_max;
    prof->j_seg[1] = 0.0;
    prof->j_seg[2] = -j_max;
    prof->j_seg[3] = 0.0;
    prof->j_seg[4] = -j_max;
    prof->j_seg[5] = 0.0;
    prof->j_seg[6] = +j_max;

    /* Обчислення початкових умов кожного сегмента */
    double cur_s = 0.0;
    double cur_v = 0.0;
    double cur_a = 0.0;
    prof->t_total = 0.0;

    for (int i = 0; i < 7; ++i) {
        prof->s_start[i] = cur_s;
        prof->v_start[i] = cur_v;
        prof->a_start[i] = cur_a;
        prof->t_total += prof->t[i];

        double dt = prof->t[i];
        double j = prof->j_seg[i];
        cur_s += cur_v * dt + 0.5 * cur_a * dt * dt + (1.0 / 6.0) * j * dt * dt * dt;
        cur_v += cur_a * dt + 0.5 * j * dt * dt;
        cur_a += j * dt;
    }

    prof->planned = true;
    return true;
}

/* Оцінка стану (положення, швидкість, прискорення) у довільний момент часу t */
motion_state_t scurve_eval(const scurve_profile_t *prof, double t) {
    motion_state_t state = {0.0, 0.0, 0.0};
    if (!prof || !prof->planned) return state;

    if (t <= 0.0) {
        state.pos = prof->start_pos;
        state.vel = 0.0;
        state.acc = 0.0;
        return state;
    }

    if (t >= prof->t_total) {
        state.pos = prof->target_pos;
        state.vel = 0.0;
        state.acc = 0.0;
        return state;
    }

    /* Пошук активного сегмента */
    double t_accum = 0.0;
    int seg = 6;
    for (int i = 0; i < 7; ++i) {
        if (t < t_accum + prof->t[i]) {
            seg = i;
            break;
        }
        t_accum += prof->t[i];
    }

    double tau = t - t_accum;
    double s0 = prof->s_start[seg];
    double v0 = prof->v_start[seg];
    double a0 = prof->a_start[seg];
    double j = prof->j_seg[seg];

    double s_rel = s0 + v0 * tau + 0.5 * a0 * tau * tau + (1.0 / 6.0) * j * tau * tau * tau;
    double v_rel = v0 + a0 * tau + 0.5 * j * tau * tau;
    double a_rel = a0 + j * tau;

    state.pos = prof->start_pos + prof->dir * s_rel;
    state.vel = prof->dir * v_rel;
    state.acc = prof->dir * a_rel;

    return state;
}
