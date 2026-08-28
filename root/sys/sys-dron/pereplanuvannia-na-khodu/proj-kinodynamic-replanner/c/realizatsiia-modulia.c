#include <stdio.h>
#include <stdbool.h>
#include <math.h>
#include <string.h>

#define MAX_SEGMENTS 8
#define SAMPLES_PER_SEGMENT 25

typedef struct {
    double x;
    double y;
    double z;
} Vec3;

static inline Vec3 vec3_make(double x, double y, double z) {
    Vec3 v = {x, y, z};
    return v;
}

static inline Vec3 vec3_add(Vec3 a, Vec3 b) {
    return vec3_make(a.x + b.x, a.y + b.y, a.z + b.z);
}

static inline Vec3 vec3_sub(Vec3 a, Vec3 b) {
    return vec3_make(a.x - b.x, a.y - b.y, a.z - b.z);
}

static inline Vec3 vec3_scale(Vec3 v, double s) {
    return vec3_make(v.x * s, v.y * s, v.z * s);
}

static inline double vec3_dot(Vec3 a, Vec3 b) {
    return a.x * b.x + a.y * b.y + a.z * b.z;
}

static inline double vec3_norm_sq(Vec3 v) {
    return vec3_dot(v, v);
}

static inline double vec3_norm(Vec3 v) {
    return sqrt(vec3_norm_sq(v));
}

static inline Vec3 vec3_cross(Vec3 a, Vec3 b) {
    return vec3_make(
        a.y * b.z - a.z * b.y,
        a.z * b.x - a.x * b.z,
        a.x * b.y - a.y * b.x
    );
}

/* Структура кінематичного стану в точці */
typedef struct {
    Vec3 pos;
    Vec3 vel;
    Vec3 acc;
    Vec3 jerk;
} KinematicState;

/* Фізичні обмеження безпілотника */
typedef struct {
    double max_vel;     /* м/с */
    double max_acc;     /* м/с² */
    double max_jerk;    /* м/с³ */
    double safe_radius; /* м */
} DroneLimits;

/* Одновимірний квінтичний поліном */
typedef struct {
    double c[6]; /* c[0] + c[1]*t + ... + c[5]*t^5 */
} Poly1D;

static void poly1d_solve(Poly1D *p, double p0, double v0, double a0,
                         double p1, double v1, double a1, double T) {
    double T2 = T * T;
    double T3 = T2 * T;
    double T4 = T3 * T;
    double T5 = T4 * T;

    p->c[0] = p0;
    p->c[1] = v0;
    p->c[2] = 0.5 * a0;

    double dp = p1 - (p0 + v0 * T + 0.5 * a0 * T2);
    double dv = v1 - (v0 + a0 * T);
    double da = a1 - a0;

    p->c[3] = (10.0 * dp - 4.0 * dv * T + 0.5 * da * T2) / T3;
    p->c[4] = (-15.0 * dp + 7.0 * dv * T - da * T2) / T4;
    p->c[5] = (6.0 * dp - 3.0 * dv * T + 0.5 * da * T2) / T5;
}

static inline double poly1d_eval_p(const Poly1D *p, double t) {
    return p->c[0] + t * (p->c[1] + t * (p->c[2] + t * (p->c[3] + t * (p->c[4] + t * p->c[5]))));
}

static inline double poly1d_eval_v(const Poly1D *p, double t) {
    return p->c[1] + t * (2.0 * p->c[2] + t * (3.0 * p->c[3] + t * (4.0 * p->c[4] + t * 5.0 * p->c[5])));
}

static inline double poly1d_eval_a(const Poly1D *p, double t) {
    return 2.0 * p->c[2] + t * (6.0 * p->c[3] + t * (12.0 * p->c[4] + t * 20.0 * p->c[5]));
}

static inline double poly1d_eval_j(const Poly1D *p, double t) {
    return 6.0 * p->c[3] + t * (24.0 * p->c[4] + t * 60.0 * p->c[5]);
}

/* 3D-сегмент траєкторії */
typedef struct {
    Poly1D px;
    Poly1D py;
    Poly1D pz;
    double duration;
    double start_time;
} Segment3D;

static void segment3d_init(Segment3D *seg, KinematicState start, KinematicState end,
                           double duration, double start_time) {
    seg->duration = duration;
    seg->start_time = start_time;
    poly1d_solve(&seg->px, start.pos.x, start.vel.x, start.acc.x, end.pos.x, end.vel.x, end.acc.x, duration);
    poly1d_solve(&seg->py, start.pos.y, start.vel.y, start.acc.y, end.pos.y, end.vel.y, end.acc.y, duration);
    poly1d_solve(&seg->pz, start.pos.z, start.vel.z, start.acc.z, end.pos.z, end.vel.z, end.acc.z, duration);
}

static KinematicState segment3d_eval(const Segment3D *seg, double global_time) {
    double t = global_time - seg->start_time;
    if (t < 0.0) t = 0.0;
    if (t > seg->duration) t = seg->duration;

    KinematicState s;
    s.pos.x = poly1d_eval_p(&seg->px, t);
    s.pos.y = poly1d_eval_p(&seg->py, t);
    s.pos.z = poly1d_eval_p(&seg->pz, t);

    s.vel.x = poly1d_eval_v(&seg->px, t);
    s.vel.y = poly1d_eval_v(&seg->py, t);
    s.vel.z = poly1d_eval_v(&seg->pz, t);

    s.acc.x = poly1d_eval_a(&seg->px, t);
    s.acc.y = poly1d_eval_a(&seg->py, t);
    s.acc.z = poly1d_eval_a(&seg->pz, t);

    s.jerk.x = poly1d_eval_j(&seg->px, t);
    s.jerk.y = poly1d_eval_j(&seg->py, t);
    s.jerk.z = poly1d_eval_j(&seg->pz, t);
    return s;
}

/* Повна траєкторія з кількох сегментів */
typedef struct {
    Segment3D segments[MAX_SEGMENTS];
    int count;
    double total_duration;
} Trajectory;

static void trajectory_clear(Trajectory *traj) {
    traj->count = 0;
    traj->total_duration = 0.0;
}

static bool trajectory_add_segment(Trajectory *traj, KinematicState start, KinematicState end, double duration) {
    if (traj->count >= MAX_SEGMENTS) return false;
    double start_time = traj->total_duration;
    segment3d_init(&traj->segments[traj->count], start, end, duration, start_time);
    traj->total_duration += duration;
    traj->count++;
    return true;
}

static KinematicState trajectory_eval(const Trajectory *traj, double t) {
    if (traj->count == 0) {
        KinematicState zero = {0};
        return zero;
    }
    if (t <= 0.0) return segment3d_eval(&traj->segments[0], 0.0);
    if (t >= traj->total_duration) {
        return segment3d_eval(&traj->segments[traj->count - 1], traj->total_duration);
    }

    for (int i = 0; i < traj->count; ++i) {
        double seg_end = traj->segments[i].start_time + traj->segments[i].duration;
        if (t <= seg_end || i == traj->count - 1) {
            return segment3d_eval(&traj->segments[i], t);
        }
    }
    return segment3d_eval(&traj->segments[traj->count - 1], traj->total_duration);
}

/* Модель сферичної перешкоди */
typedef struct {
    Vec3 center;
    double radius;
} SphereObstacle;

static bool check_collision_segment(const Segment3D *seg, const SphereObstacle *obs, double safe_margin, double *t_col_out) {
    for (int i = 0; i <= SAMPLES_PER_SEGMENT; ++i) {
        double t = seg->start_time + (seg->duration * i) / SAMPLES_PER_SEGMENT;
        KinematicState st = segment3d_eval(seg, t);
        double dist = vec3_norm(vec3_sub(st.pos, obs->center));
        if (dist < (obs->radius + safe_margin)) {
            if (t_col_out) *t_col_out = t;
            return true;
        }
    }
    return false;
}

/* Перевірка кінодинамічних лімітів */
static bool check_and_rescale_segment(Segment3D *seg, const DroneLimits *lim, int max_iter) {
    for (int iter = 0; iter < max_iter; ++iter) {
        double max_v = 0.0;
        double max_a = 0.0;

        for (int i = 0; i <= SAMPLES_PER_SEGMENT; ++i) {
            double t = seg->start_time + (seg->duration * i) / SAMPLES_PER_SEGMENT;
            KinematicState st = segment3d_eval(seg, t);
            double v_mag = vec3_norm(st.vel);
            double a_mag = vec3_norm(st.acc);
            if (v_mag > max_v) max_v = v_mag;
            if (a_mag > max_a) max_a = a_mag;
        }

        if (max_v <= lim->max_vel && max_a <= lim->max_acc) {
            return true;
        }

        double scale_v = max_v / lim->max_vel;
        double scale_a = sqrt(max_a / lim->max_acc);
        double scale = (scale_v > scale_a) ? scale_v : scale_a;
        if (scale < 1.05) scale = 1.05;

        KinematicState s0 = segment3d_eval(seg, seg->start_time);
        KinematicState s1 = segment3d_eval(seg, seg->start_time + seg->duration);
        double new_dur = seg->duration * scale;
        segment3d_init(seg, s0, s1, new_dur, seg->start_time);
    }
    return false;
}

/* Рушій динамічного перепланування */
typedef struct {
    DroneLimits limits;
    double plan_budget_sec; /* t_plan */
} Replanner;

static void replanner_init(Replanner *r, DroneLimits lim, double budget) {
    r->limits = lim;
    r->plan_budget_sec = budget;
}

/* Виконати C²-перепланування на ходу при виявленні перешкоди */
static bool replanner_replan(const Replanner *r,
                             const Trajectory *active_traj,
                             double t_now,
                             const SphereObstacle *obs,
                             Vec3 goal_pos,
                             Trajectory *new_traj_out) {
    /* 1. Обчислюємо момент та стан склеювання */
    double t_stitch = t_now + r->plan_budget_sec;
    KinematicState s_stitch = trajectory_eval(active_traj, t_stitch);

    /* 2. Обчислюємо вектор ухилення: відхилення перпендикулярно до лінії руху */
    Vec3 dir = vec3_sub(obs->center, s_stitch.pos);
    double dist_to_obs = vec3_norm(dir);
    if (dist_to_obs < 0.001) dir = vec3_make(1.0, 0.0, 0.0);
    else dir = vec3_scale(dir, 1.0 / dist_to_obs);

    /* Ортогональний вектор відхилення (убік по горизонталі) */
    Vec3 up = vec3_make(0.0, 0.0, 1.0);
    Vec3 lateral = vec3_cross(dir, up);
    if (vec3_norm_sq(lateral) < 0.01) lateral = vec3_make(0.0, 1.0, 0.0);
    else lateral = vec3_scale(lateral, 1.0 / vec3_norm(lateral));

    /* Точка обходу на безпечній відстані збоку від перешкоди */
    double detour_offset = obs->radius + r->limits.safe_radius + 0.8;
    Vec3 detour_pos = vec3_add(obs->center, vec3_scale(lateral, detour_offset));

    /* Швидкість у точці обходу зберігає напрямок та величину */
    Vec3 detour_vel = vec3_scale(s_stitch.vel, 0.9);
    Vec3 detour_acc = vec3_make(0.0, 0.0, 0.0);

    KinematicState s_detour;
    s_detour.pos = detour_pos;
    s_detour.vel = detour_vel;
    s_detour.acc = detour_acc;
    s_detour.jerk = vec3_make(0.0, 0.0, 0.0);

    /* Кінцевий стан у глобальній цілі */
    KinematicState s_goal;
    s_goal.pos = goal_pos;
    s_goal.vel = vec3_make(0.0, 0.0, 0.0);
    s_goal.acc = vec3_make(0.0, 0.0, 0.0);
    s_goal.jerk = vec3_make(0.0, 0.0, 0.0);

    /* 3. Генерація двосегментного сплайна: стик -> обхід -> фініш */
    trajectory_clear(new_traj_out);

    double d1 = vec3_norm(vec3_sub(s_detour.pos, s_stitch.pos));
    double d2 = vec3_norm(vec3_sub(s_goal.pos, s_detour.pos));
    double dur1 = fmax(d1 / (r->limits.max_vel * 0.75), 0.5);
    double dur2 = fmax(d2 / (r->limits.max_vel * 0.75), 0.5);

    trajectory_add_segment(new_traj_out, s_stitch, s_detour, dur1);
    trajectory_add_segment(new_traj_out, s_detour, s_goal, dur2);

    /* 4. Кінодинамічна верифікація та корекція тривалості сегментів */
    for (int i = 0; i < new_traj_out->count; ++i) {
        check_and_rescale_segment(&new_traj_out->segments[i], &r->limits, 10);
    }
    return true;
}

int main(void) {
    printf("=== Kinodynamic Replanner Demo (C99) ===\n");

    DroneLimits lim = {
        .max_vel = 12.0,      /* 12 м/с */
        .max_acc = 8.0,       /* 8 м/с² */
        .max_jerk = 25.0,     /* 25 м/с³ */
        .safe_radius = 0.6    /* 0.6 м */
    };

    Replanner replanner;
    replanner_init(&replanner, lim, 0.030); /* 30 мс бюджет планування */

    /* Початкова траєкторія: прямий політ по осі X від (0,0,2) до (20,0,2) */
    Trajectory initial_traj;
    trajectory_clear(&initial_traj);

    KinematicState start_st = {
        .pos = {0.0, 0.0, 2.0},
        .vel = {10.0, 0.0, 0.0},
        .acc = {0.0, 0.0, 0.0},
        .jerk = {0.0, 0.0, 0.0}
    };
    KinematicState end_st = {
        .pos = {20.0, 0.0, 2.0},
        .vel = {10.0, 0.0, 0.0},
        .acc = {0.0, 0.0, 0.0},
        .jerk = {0.0, 0.0, 0.0}
    };
    trajectory_add_segment(&initial_traj, start_st, end_st, 2.0);

    /* Раптова перешкода попереду на позиції (8, 0, 2) радіусом 1.0 м */
    SphereObstacle obstacle = {
        .center = {8.0, 0.0, 2.0},
        .radius = 1.0
    };

    /* Момент виявлення t_now = 0.200 с */
    double t_now = 0.200;
    double t_col = 0.0;
    bool col = check_collision_segment(&initial_traj.segments[0], &obstacle, lim.safe_radius, &t_col);
    printf("Виявлено колізію на старій траєкторії при t = %.3f с (дистанція до зіткнення)\n", t_col);

    Trajectory new_traj;
    bool ok = replanner_replan(&replanner, &initial_traj, t_now, &obstacle, end_st.pos, &new_traj);

    if (ok) {
        printf("Успішне C²-склеювання траєкторії:\n");
        printf("  Старт склеювання t_stitch = %.3f с\n", t_now + replanner.plan_budget_sec);
        printf("  Кількість нових сегментів: %d, сумарний час: %.3f с\n\n",
               new_traj.count, new_traj.total_duration);

        /* Друк точок нової траєкторії */
        printf(" Час (с) | Позиція X (м) | Позиція Y (м) | Швидкість (м/с) | Прискорення (м/с²)\n");
        printf("-----------------------------------------------------------------------------\n");
        for (double t = 0.0; t <= new_traj.total_duration; t += 0.25) {
            KinematicState st = trajectory_eval(&new_traj, t);
            printf(" %7.3f | %13.3f | %13.3f | %15.3f | %18.3f\n",
                   t, st.pos.x, st.pos.y, vec3_norm(st.vel), vec3_norm(st.acc));
        }
    }
    return 0;
}
