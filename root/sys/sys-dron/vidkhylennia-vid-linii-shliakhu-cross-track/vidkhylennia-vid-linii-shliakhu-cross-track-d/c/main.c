#include <math.h>
#include <stdbool.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef struct {
    double x;
    double y;
} vec2_d;

typedef struct {
    double lookahead_dist; /* Базове випередження Delta_los [м] */
    double lookahead_time; /* Коефіцієнт часу Delta = v * k_t [с] */
    double min_lookahead;  /* Мінімальне випередження [м] */
    double max_lookahead;  /* Максимальне випередження [м] */
    double ki;             /* Коефіцієнт інтегратора вітру [1/с] */
    double int_limit;      /* Поріг інтегратора [м*с] */
    double max_cross_ang;  /* Максимальний кут захоплення лінії [рад] */
} crosstrack_cfg_t;

typedef struct {
    double ect;            /* Поперечна похибка e_ct зі знаком [м] */
    double along_track;    /* Поздовжня пройдена відстань s [м] */
    double progress;       /* Параметр відрізка u in [0, 1] */
    vec2_d proj_pt;        /* Точка ортогональної проєкції p_proj [м] */
    double course_cmd;     /* Командний шляховий курс chi_cmd [рад] */
    double curvature_cmd;  /* Бажана кривина траєкторії kappa [1/м] */
} crosstrack_out_t;

static inline double math_wrap_pi(double rad) {
    while (rad > M_PI) rad -= 2.0 * M_PI;
    while (rad < -M_PI) rad += 2.0 * M_PI;
    return rad;
}

static inline double math_clamp(double v, double min_v, double max_v) {
    if (v < min_v) return min_v;
    if (v > max_v) return max_v;
    return v;
}

bool calculate_crosstrack_guidance(vec2_d pos,
                                   vec2_d wa,
                                   vec2_d wb,
                                   double ground_speed,
                                   double dt,
                                   const crosstrack_cfg_t *cfg,
                                   double *integrator_state,
                                   crosstrack_out_t *out) {
    /* 1. Вектор відрізка b = WB - WA */
    double bx = wb.x - wa.x;
    double by = wb.y - wa.y;
    double seg_len = sqrt(bx * bx + by * by);

    if (seg_len < 1e-6) {
        return false; /* Некоректний сегмент нульової довжини */
    }

    /* 2. Одиничний дотичний вектор t̂ = b / seg_len */
    double tx = bx / seg_len;
    double ty = by / seg_len;

    /* 3. Вектор положення від початку a = pos - WA */
    double ax = pos.x - wa.x;
    double ay = pos.y - wa.y;

    /* 4. Поперечна похибка e_ct через 2D-векторний добуток a × t̂ */
    double ect = ax * ty - ay * tx;

    /* 5. Поздовжня пройдена відстань s = a · t̂ */
    double s = ax * tx + ay * ty;
    double u = s / seg_len;

    /* 6. Координати точки проєкції */
    vec2_d proj = { wa.x + s * tx, wa.y + s * ty };

    /* 7. Адаптивна дистанція прямої видимості */
    double delta_los = ground_speed * cfg->lookahead_time;
    if (delta_los < cfg->lookahead_dist) {
        delta_los = cfg->lookahead_dist;
    }
    delta_los = math_clamp(delta_los, cfg->min_lookahead, cfg->max_lookahead);

    /* 8. Інтегрування похибки для компенсації вітру (ILOS) */
    if (integrator_state != NULL && dt > 0.0) {
        *integrator_state += ect * dt;
        *integrator_state = math_clamp(*integrator_state, -cfg->int_limit, cfg->int_limit);
    }
    double int_val = (integrator_state != NULL) ? *integrator_state : 0.0;
    double ect_eff = ect + cfg->ki * int_val;

    /* 9. Розрахунок кута корекції та командного курсу */
    double chi_f = atan2(by, bx);
    double chi_cross = atan(-ect_eff / delta_los);
    chi_cross = math_clamp(chi_cross, -cfg->max_cross_ang, cfg->max_cross_ang);

    double chi_cmd = math_wrap_pi(chi_f + chi_cross);
    double kappa = 2.0 * sin(chi_cross) / delta_los;

    /* 10. Запис результатів */
    out->ect = ect;
    out->along_track = s;
    out->progress = u;
    out->proj_pt = proj;
    out->course_cmd = chi_cmd;
    out->curvature_cmd = kappa;

    return true;
}
