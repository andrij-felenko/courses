#include <stdio.h>
#include <stdbool.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef struct {
    double x;
    double y;
} vec2_t;

typedef struct {
    vec2_t pos;
    double acceptance_radius;
} waypoint_t;

typedef struct {
    double lookahead_distance; /* Базова дистанція випередження Delta_los [м] */
    double lookahead_time;     /* Динамічний час випередження Delta = v * k_t [с] */
    double min_lookahead;      /* Мінімальне обмеження Delta [м] */
    double max_lookahead;      /* Максимальне обмеження Delta [м] */
    double ki_cross_track;     /* Коефіцієнт інтегратора вітру k_i [1/с] */
    double integrator_max;     /* Поріг насичення інтегратора [м*с] */
    double max_approach_angle; /* Максимальний кут захоплення лінії [рад] */
} los_config_t;

typedef struct {
    double cross_track_error;   /* Поперечне відхилення e_ct зі знаком [м] */
    double along_track_dist;    /* Пройдена відстань уздовж відрізка s [м] */
    double normalized_progress; /* Параметр відрізка u in [0, 1] */
    vec2_t projection_point;    /* Координати проєкції p_proj [м] */
    double segment_length;      /* Довжина поточного відрізка [м] */
    double segment_course;      /* Азимут лінії шляху chi_F [рад] */
    double command_course;      /* Бажаний шляховий курс chi_cmd [рад] */
    double curvature_cmd;       /* Бажана кривина траєкторії kappa [1/м] */
    size_t current_segment_idx; /* Індекс поточної цільової точки */
    bool mission_completed;     /* Прапорець завершення маршруту */
} guidance_state_t;

typedef struct {
    los_config_t config;
    guidance_state_t state;
    double cross_track_integral;
    const waypoint_t *waypoints;
    size_t waypoint_count;
} track_controller_t;

/* Допоміжні векторні операції */
static inline vec2_t vec2_sub(vec2_t a, vec2_t b) {
    return (vec2_t){ a.x - b.x, a.y - b.y };
}

static inline vec2_t vec2_add(vec2_t a, vec2_t b) {
    return (vec2_t){ a.x + b.x, a.y + b.y };
}

static inline vec2_t vec2_scale(vec2_t a, double s) {
    return (vec2_t){ a.x * s, a.y * s };
}

static inline double vec2_dot(vec2_t a, vec2_t b) {
    return a.x * b.x + a.y * b.y;
}

static inline double vec2_cross_2d(vec2_t a, vec2_t b) {
    return a.x * b.y - a.y * b.x;
}

static inline double vec2_norm(vec2_t a) {
    return sqrt(a.x * a.x + a.y * a.y);
}

static inline double wrap_to_pi(double angle) {
    while (angle > M_PI) angle -= 2.0 * M_PI;
    while (angle < -M_PI) angle += 2.0 * M_PI;
    return angle;
}

static inline double clamp_val(double val, double min_v, double max_v) {
    if (val < min_v) return min_v;
    if (val > max_v) return max_v;
    return val;
}

/* Ініціалізація контролера ведення по шляху */
void track_controller_init(track_controller_t *ctrl,
                           const waypoint_t *waypoints,
                           size_t count,
                           los_config_t config) {
    ctrl->waypoints = waypoints;
    ctrl->waypoint_count = count;
    ctrl->config = config;
    ctrl->cross_track_integral = 0.0;

    ctrl->state.cross_track_error = 0.0;
    ctrl->state.along_track_dist = 0.0;
    ctrl->state.normalized_progress = 0.0;
    ctrl->state.projection_point = (vec2_t){ 0.0, 0.0 };
    ctrl->state.segment_length = 0.0;
    ctrl->state.segment_course = 0.0;
    ctrl->state.command_course = 0.0;
    ctrl->state.curvature_cmd = 0.0;
    ctrl->state.current_segment_idx = 0;
    ctrl->state.mission_completed = (count < 2);
}

/* Розрахунок геометрії відрізка та поперечного відхилення */
static bool calculate_segment_geometry(vec2_t pos,
                                       vec2_t wa,
                                       vec2_t wb,
                                       double *out_ect,
                                       double *out_s,
                                       double *out_u,
                                       vec2_t *out_proj,
                                       double *out_len,
                                       double *out_chi_f) {
    vec2_t b = vec2_sub(wb, wa);
    double len = vec2_norm(b);

    if (len < 1e-6) {
        return false; /* Збіг точок, нульова довжина сегмента */
    }

    vec2_t a = vec2_sub(pos, wa);
    vec2_t t_hat = vec2_scale(b, 1.0 / len);

    /* 1. Поперечне відхилення через 2D-псевдоскалярний добуток */
    double cross = vec2_cross_2d(a, b);
    double ect = cross / len;

    /* 2. Поздовжня відстань уздовж лінії */
    double s = vec2_dot(a, t_hat);
    double u = s / len;

    /* 3. Координати точки проєкції */
    vec2_t proj = vec2_add(wa, vec2_scale(t_hat, s));

    *out_ect = ect;
    *out_s = s;
    *out_u = u;
    *out_proj = proj;
    *out_len = len;
    *out_chi_f = atan2(b.y, b.x);

    return true;
}

/* Крок контуру наведення: перевірка перемикання та закон ILOS */
void track_controller_update(track_controller_t *ctrl,
                             vec2_t current_pos,
                             double ground_speed,
                             double dt) {
    if (ctrl->state.mission_completed || ctrl->waypoint_count < 2) {
        return;
    }

    size_t idx = ctrl->state.current_segment_idx;
    vec2_t wa = ctrl->waypoints[idx].pos;
    vec2_t wb = ctrl->waypoints[idx + 1].pos;
    double r_acc = ctrl->waypoints[idx + 1].acceptance_radius;

    double ect = 0.0, s = 0.0, u = 0.0, len = 0.0, chi_f = 0.0;
    vec2_t proj = { 0.0, 0.0 };

    if (!calculate_segment_geometry(current_pos, wa, wb, &ect, &s, &u, &proj, &len, &chi_f)) {
        /* Пропускаємо некоректний сегмент */
        ctrl->state.current_segment_idx++;
        if (ctrl->state.current_segment_idx >= ctrl->waypoint_count - 1) {
            ctrl->state.mission_completed = true;
        }
        return;
    }

    /* Перевірка досягнення цільової точки WB:
       1) Дрон увійшов у радіус захоплення r_acc;
       2) АБО дрон перетнув площину нормалі (s >= len). */
    vec2_t dist_to_wb = vec2_sub(current_pos, wb);
    bool in_radius = vec2_norm(dist_to_wb) <= r_acc;
    bool passed_bisector = (s >= len);

    if (in_radius || passed_bisector) {
        if (idx + 2 < ctrl->waypoint_count) {
            ctrl->state.current_segment_idx++;
            idx = ctrl->state.current_segment_idx;
            wa = ctrl->waypoints[idx].pos;
            wb = ctrl->waypoints[idx + 1].pos;
            calculate_segment_geometry(current_pos, wa, wb, &ect, &s, &u, &proj, &len, &chi_f);
        } else {
            ctrl->state.mission_completed = true;
        }
    }

    /* Адаптивна дистанція випередження Delta_los = max(min, speed * k_t) */
    double delta_los = ground_speed * ctrl->config.lookahead_time;
    if (delta_los < ctrl->config.lookahead_distance) {
        delta_los = ctrl->config.lookahead_distance;
    }
    delta_los = clamp_val(delta_los, ctrl->config.min_lookahead, ctrl->config.max_lookahead);

    /* Інтегратор вітру з анти-вінд-ап захистом */
    ctrl->cross_track_integral += ect * dt;
    ctrl->cross_track_integral = clamp_val(ctrl->cross_track_integral,
                                           -ctrl->config.integrator_max,
                                           ctrl->config.integrator_max);

    /* Ефективне відхилення з урахуванням накопиченого дрейфу */
    double ect_effective = ect + ctrl->config.ki_cross_track * ctrl->cross_track_integral;

    /* Закон корекції курсу ILOS */
    double chi_cross = atan(-ect_effective / delta_los);
    chi_cross = clamp_val(chi_cross, -ctrl->config.max_approach_angle, ctrl->config.max_approach_angle);

    double chi_cmd = wrap_to_pi(chi_f + chi_cross);

    /* Кривина для контуру поперечного прискорення: kappa = 2 * sin(chi_cross) / delta_los */
    double kappa = 2.0 * sin(chi_cross) / delta_los;

    /* Запис стану */
    ctrl->state.cross_track_error = ect;
    ctrl->state.along_track_dist = s;
    ctrl->state.normalized_progress = u;
    ctrl->state.projection_point = proj;
    ctrl->state.segment_length = len;
    ctrl->state.segment_course = chi_f;
    ctrl->state.command_course = chi_cmd;
    ctrl->state.curvature_cmd = kappa;
}

int main(void) {
    const waypoint_t mission[] = {
        { .pos = { 0.0, 0.0 },       .acceptance_radius = 15.0 },
        { .pos = { 500.0, 0.0 },     .acceptance_radius = 20.0 },
        { .pos = { 500.0, 400.0 },   .acceptance_radius = 20.0 },
        { .pos = { 1000.0, 400.0 },  .acceptance_radius = 20.0 }
    };
    size_t wp_count = sizeof(mission) / sizeof(mission[0]);

    los_config_t cfg = {
        .lookahead_distance = 35.0,
        .lookahead_time = 2.5,
        .min_lookahead = 20.0,
        .max_lookahead = 120.0,
        .ki_cross_track = 0.03,
        .integrator_max = 50.0,
        .max_approach_angle = 55.0 * (M_PI / 180.0)
    };

    track_controller_t controller;
    track_controller_init(&controller, mission, wp_count, cfg);

    /* Початковий стан дрона: зміщення вправо на 25 метрів */
    vec2_t pos = { 10.0, 25.0 };
    double speed = 16.0; /* 16 м/с (57.6 км/год) */
    double course = 0.0;
    double dt = 0.1;

    printf("=== Симуляція ведення по місії (ILOS Cross-Track) ===\n");
    printf("Час [с] | X [м]    | Y [м]   | e_ct [м] | s [м]   | Курс [°] | Ціль [°] | Сегмент\n");
    printf("-----------------------------------------------------------------------------\n");

    for (int step = 0; step <= 350; ++step) {
        double sim_time = step * dt;

        track_controller_update(&controller, pos, speed, dt);

        if (step % 25 == 0) {
            printf("%7.1f | %7.1f | %7.1f | %8.2f | %7.1f | %8.1f | %8.1f | %zu -> %zu\n",
                   sim_time,
                   pos.x,
                   pos.y,
                   controller.state.cross_track_error,
                   controller.state.along_track_dist,
                   course * (180.0 / M_PI),
                   controller.state.command_course * (180.0 / M_PI),
                   controller.state.current_segment_idx,
                   controller.state.current_segment_idx + 1);
        }

        if (controller.state.mission_completed) {
            printf("Маршрут успішно завершено у часі %.1f с.\n", sim_time);
            break;
        }

        /* Проста динаміка відстеження курсу дроном (стала часу 0.6 с) */
        double course_err = wrap_to_pi(controller.state.command_course - course);
        course += (course_err / 0.6) * dt;
        course = wrap_to_pi(course);

        /* Інтегрування положення */
        pos.x += speed * cos(course) * dt;
        pos.y += speed * sin(course) * dt;
    }

    return 0;
}
