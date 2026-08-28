#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <math.h>

#define MAX_WAYPOINTS 64
#define EPSILON 1e-6f

typedef struct {
    float x;
    float y;
    float z;
} Vec3;

static inline Vec3 vec3_add(Vec3 a, Vec3 b) {
    return (Vec3){a.x + b.x, a.y + b.y, a.z + b.z};
}

static inline Vec3 vec3_sub(Vec3 a, Vec3 b) {
    return (Vec3){a.x - b.x, a.y - b.y, a.z - b.z};
}

static inline Vec3 vec3_scale(Vec3 a, float s) {
    return (Vec3){a.x * s, a.y * s, a.z * s};
}

static inline float vec3_dot(Vec3 a, Vec3 b) {
    return a.x * b.x + a.y * b.y + a.z * b.z;
}

static inline Vec3 vec3_cross(Vec3 a, Vec3 b) {
    return (Vec3){
        a.y * b.z - a.z * b.y,
        a.z * b.x - a.x * b.z,
        a.x * b.y - a.y * b.x
    };
}

static inline float vec3_norm(Vec3 a) {
    return sqrtf(vec3_dot(a, a));
}

static inline Vec3 vec3_normalize(Vec3 a) {
    float n = vec3_norm(a);
    if (n < EPSILON) return (Vec3){0.0f, 0.0f, 0.0f};
    return vec3_scale(a, 1.0f / n);
}

typedef struct {
    Vec3 pos;
    Vec3 vel;
    Vec3 acc;
    float jerk_mag;
} Setpoint;

typedef struct {
    float max_vel;
    float max_acc;
    float max_lat_acc;
    float max_jerk;
    float corner_radius;
} TrajectoryConfig;

typedef enum {
    SEG_STRAIGHT,
    SEG_ARC
} SegmentType;

typedef struct {
    SegmentType type;
    float length;
    float start_dist;
    float v_start;
    float v_end;
    float duration;

    // Параметри для прямолінійного сегмента
    Vec3 p_start;
    Vec3 dir;

    // Параметри для дугового сегмента
    Vec3 arc_center;
    Vec3 n_in;       // нормаль від T1 до центра дуги
    Vec3 binormal;   // вісь обертання площини дуги
    float radius;
    float angle;
} TrajectorySegment;

typedef struct {
    TrajectoryConfig config;
    Vec3 waypoints[MAX_WAYPOINTS];
    size_t num_waypoints;

    TrajectorySegment segments[MAX_WAYPOINTS * 2];
    size_t num_segments;
    float total_distance;
    float total_duration;
} TrajectoryPlanner;

void planner_init(TrajectoryPlanner* p, TrajectoryConfig cfg) {
    p->config = cfg;
    p->num_waypoints = 0;
    p->num_segments = 0;
    p->total_distance = 0.0f;
    p->total_duration = 0.0f;
}

bool planner_add_waypoint(TrajectoryPlanner* p, Vec3 wp) {
    if (p->num_waypoints >= MAX_WAYPOINTS) return false;
    if (p->num_waypoints > 0) {
        Vec3 diff = vec3_sub(wp, p->waypoints[p->num_waypoints - 1]);
        if (vec3_norm(diff) < 1e-2f) return false; // ігноруємо близькі дублікати
    }
    p->waypoints[p->num_waypoints++] = wp;
    return true;
}

bool planner_generate(TrajectoryPlanner* p) {
    if (p->num_waypoints < 2) return false;
    p->num_segments = 0;

    size_t nw = p->num_waypoints;
    float d_lead[MAX_WAYPOINTS] = {0};
    float r_eff[MAX_WAYPOINTS] = {0};
    float theta[MAX_WAYPOINTS] = {0};
    Vec3 u_seg[MAX_WAYPOINTS];
    float seg_len[MAX_WAYPOINTS];

    for (size_t i = 0; i < nw - 1; ++i) {
        Vec3 diff = vec3_sub(p->waypoints[i + 1], p->waypoints[i]);
        seg_len[i] = vec3_norm(diff);
        u_seg[i] = vec3_scale(diff, 1.0f / seg_len[i]);
    }

    // 1. Геометричний розрахунок скруглень на кутах
    for (size_t i = 1; i < nw - 1; ++i) {
        float cos_t = vec3_dot(u_seg[i - 1], u_seg[i]);
        if (cos_t > 0.9999f) {
            theta[i] = 0.0f;
            d_lead[i] = 0.0f;
            r_eff[i] = 0.0f;
            continue;
        }
        if (cos_t < -0.9999f) cos_t = -0.9999f;
        theta[i] = acosf(cos_t);

        float half_t = theta[i] * 0.5f;
        float d_nom = p->config.corner_radius * tanf(half_t);

        // Обмеження відступу połовиною найкоротшого із сусідніх відрізків
        float max_d = 0.45f * fminf(seg_len[i - 1], seg_len[i]);
        float scale = (d_nom > max_d) ? (max_d / d_nom) : 1.0f;

        r_eff[i] = p->config.corner_radius * scale;
        d_lead[i] = r_eff[i] * tanf(half_t);
    }

    // 2. Побудова послідовності сегментів траєкторії
    float cur_dist = 0.0f;
    for (size_t i = 0; i < nw - 1; ++i) {
        float start_trim = (i == 0) ? 0.0f : d_lead[i];
        float end_trim = (i == nw - 2) ? 0.0f : d_lead[i + 1];
        float straight_len = seg_len[i] - start_trim - end_trim;

        if (straight_len > EPSILON) {
            TrajectorySegment* s = &p->segments[p->num_segments++];
            s->type = SEG_STRAIGHT;
            s->length = straight_len;
            s->start_dist = cur_dist;
            s->dir = u_seg[i];
            s->p_start = vec3_add(p->waypoints[i], vec3_scale(u_seg[i], start_trim));
            cur_dist += straight_len;
        }

        // Вставка дуги скруглення після прямого відрізка
        if (i < nw - 2 && theta[i + 1] > 1e-3f) {
            size_t idx = i + 1;
            TrajectorySegment* s = &p->segments[p->num_segments++];
            s->type = SEG_ARC;
            s->length = r_eff[idx] * theta[idx];
            s->start_dist = cur_dist;
            s->radius = r_eff[idx];
            s->angle = theta[idx];

            Vec3 t1 = vec3_sub(p->waypoints[idx], vec3_scale(u_seg[i], d_lead[idx]));
            Vec3 b = vec3_normalize(vec3_cross(u_seg[i], u_seg[i + 1]));
            s->binormal = b;
            s->n_in = vec3_normalize(vec3_cross(b, u_seg[i]));
            s->arc_center = vec3_add(t1, vec3_scale(s->n_in, s->radius));
            s->p_start = t1;

            cur_dist += s->length;
        }
    }
    p->total_distance = cur_dist;

    // 3. Профілювання швидкості (трапецоїд із лімітом бічного прискорення)
    for (size_t i = 0; i < p->num_segments; ++i) {
        TrajectorySegment* s = &p->segments[i];
        if (s->type == SEG_ARC) {
            float v_corn = sqrtf(p->config.max_lat_acc * s->radius);
            s->v_start = fminf(p->config.max_vel, v_corn);
            s->v_end = s->v_start;
        } else {
            s->v_start = p->config.max_vel;
            s->v_end = p->config.max_vel;
        }
    }
    p->segments[0].v_start = 0.0f;
    p->segments[p->num_segments - 1].v_end = 0.0f;

    // Зворотний прохід (Backward Pass: розрахунок точок гальмування)
    for (int i = (int)p->num_segments - 2; i >= 0; --i) {
        float max_v = sqrtf(p->segments[i + 1].v_start * p->segments[i + 1].v_start +
                            2.0f * p->config.max_acc * p->segments[i].length);
        p->segments[i].v_end = fminf(p->segments[i].v_end, p->segments[i + 1].v_start);
        p->segments[i].v_start = fminf(p->segments[i].v_start, max_v);
    }

    // Прямий прохід (Forward Pass: розрахунок розгону та тривалостей)
    float total_t = 0.0f;
    for (size_t i = 0; i < p->num_segments; ++i) {
        TrajectorySegment* s = &p->segments[i];
        float max_v = sqrtf(s->v_start * s->v_start + 2.0f * p->config.max_acc * s->length);
        s->v_end = fminf(s->v_end, max_v);

        float v_avg = 0.5f * (s->v_start + s->v_end);
        if (v_avg < 1e-2f) v_avg = 1e-2f;
        s->duration = s->length / v_avg;
        total_t += s->duration;
    }
    p->total_duration = total_t;

    return true;
}

Setpoint planner_sample(const TrajectoryPlanner* p, float t) {
    Setpoint sp = {0};
    if (p->num_segments == 0) return sp;

    if (t <= 0.0f) {
        sp.pos = p->segments[0].p_start;
        return sp;
    }

    float t_acc = 0.0f;
    for (size_t i = 0; i < p->num_segments; ++i) {
        const TrajectorySegment* s = &p->segments[i];
        if (t <= t_acc + s->duration || i == p->num_segments - 1) {
            float tau = (s->duration > EPSILON) ? (t - t_acc) / s->duration : 1.0f;
            if (tau > 1.0f) tau = 1.0f;

            float cur_v = s->v_start + (s->v_end - s->v_start) * tau;
            float cur_a = (s->duration > EPSILON) ? (s->v_end - s->v_start) / s->duration : 0.0f;
            float local_s = s->v_start * (t - t_acc) + 0.5f * cur_a * (t - t_acc) * (t - t_acc);

            if (s->type == SEG_STRAIGHT) {
                sp.pos = vec3_add(s->p_start, vec3_scale(s->dir, local_s));
                sp.vel = vec3_scale(s->dir, cur_v);
                sp.acc = vec3_scale(s->dir, cur_a);
            } else {
                float phi = (s->radius > EPSILON) ? (local_s / s->radius) : 0.0f;
                // Обертання нормалі n_in навколо бінормалі на кут phi
                Vec3 radial = vec3_add(
                    vec3_scale(s->n_in, -cosf(phi)),
                    vec3_scale(vec3_cross(s->binormal, s->n_in), sinf(phi))
                );
                sp.pos = vec3_add(s->arc_center, vec3_scale(radial, s->radius));

                Vec3 tangent = vec3_cross(s->binormal, radial);
                sp.vel = vec3_scale(tangent, cur_v);

                Vec3 a_tan = vec3_scale(tangent, cur_a);
                Vec3 a_centripetal = vec3_scale(radial, -(cur_v * cur_v) / s->radius);
                sp.acc = vec3_add(a_tan, a_centripetal);
            }
            return sp;
        }
        t_acc += s->duration;
    }

    sp.pos = p->waypoints[p->num_waypoints - 1];
    return sp;
}

int main(void) {
    TrajectoryPlanner planner;
    TrajectoryConfig cfg = {
        .max_vel = 12.0f,
        .max_acc = 4.0f,
        .max_lat_acc = 6.0f,
        .max_jerk = 20.0f,
        .corner_radius = 8.0f
    };

    planner_init(&planner, cfg);
    planner_add_waypoint(&planner, (Vec3){0.0f, 0.0f, 10.0f});
    planner_add_waypoint(&planner, (Vec3){50.0f, 0.0f, 10.0f});
    planner_add_waypoint(&planner, (Vec3){50.0f, 50.0f, 15.0f});
    planner_add_waypoint(&planner, (Vec3){0.0f, 50.0f, 15.0f});

    if (!planner_generate(&planner)) {
        printf("Помилка планування траєкторії.\n");
        return 1;
    }

    printf("Траєкторія успішно згенерована:\n");
    printf("  Сегментів: %zu, Загальна дистанція: %.2f м, Час: %.2f с\n\n",
           planner.num_segments, planner.total_distance, planner.total_duration);

    for (float t = 0.0f; t <= planner.total_duration + 0.1f; t += 0.5f) {
        Setpoint sp = planner_sample(&planner, t);
        printf("t = %5.2f c | Поз: (%6.2f, %6.2f, %5.2f) м | Швидк: %5.2f м/с | Приск: %5.2f м/с²\n",
               t, sp.pos.x, sp.pos.y, sp.pos.z, vec3_norm(sp.vel), vec3_norm(sp.acc));
    }

    return 0;
}
