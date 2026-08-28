#define _POSIX_C_SOURCE 199309L
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdint.h>
#include <string.h>
#include <math.h>
#include <time.h>

#define MAX_WAYPOINTS       32
#define MAX_POLY_SEGMENTS   16
#define MAX_OBSTACLES       64
#define POLY_ORDER          6   /* Поліном 5-го степеня: 6 коефіцієнтів [c0..c5] */

/* Просторова точка / 3D-вектор */
typedef struct {
    double x;
    double y;
    double z;
} Vec3;

static inline Vec3 vec3_add(Vec3 a, Vec3 b) { return (Vec3){a.x + b.x, a.y + b.y, a.z + b.z}; }
static inline Vec3 vec3_sub(Vec3 a, Vec3 b) { return (Vec3){a.x - b.x, a.y - b.y, a.z - b.z}; }
static inline Vec3 vec3_scale(Vec3 v, double s) { return (Vec3){v.x * s, v.y * s, v.z * s}; }
static inline double vec3_dot(Vec3 a, Vec3 b) { return a.x * b.x + a.y * b.y + a.z * b.z; }
static inline double vec3_norm(Vec3 v) { return sqrt(vec3_dot(v, v)); }

/* Повний кінематичний стан дрона */
typedef struct {
    Vec3 pos;       /* Позиція [м] */
    Vec3 vel;       /* Швидкість [м/с] */
    Vec3 acc;       /* Прискорення [м/с²] */
    double yaw;     /* Кут курсу [рад] */
} DroneState;

/* Обмеження динаміки апарата */
typedef struct {
    double max_vel;     /* Максимальна швидкість [м/с] */
    double max_acc;     /* Максимальне прискорення [м/с²] */
    double max_jerk;    /* Максимальний ривок [м/с³] */
    double safety_dist; /* Радіус захисної сфери дрона [м] */
} DroneLimits;

/* Сферична перешкода для просторової перевірки */
typedef struct {
    Vec3 center;
    double radius;
} SphereObstacle;

/* Опуклий осередок безпечного коридору (Safe Flight Corridor box) */
typedef struct {
    Vec3 min_bound;
    Vec3 max_bound;
} SafeBox;

/* Одновимірний поліном 5-го степеня: p(t) = c0 + c1*t + c2*t² + c3*t³ + c4*t⁴ + c5*t⁵ */
typedef struct {
    double c[POLY_ORDER];
} Poly1D;

/* 3D-сегмент траєкторії */
typedef struct {
    Poly1D px;
    Poly1D py;
    Poly1D pz;
    double duration; /* Тривалість сегмента [с] */
} TrajectorySegment;

/* Повна траєкторія з метаданими якості */
typedef struct {
    TrajectorySegment segments[MAX_POLY_SEGMENTS];
    size_t num_segments;
    double total_duration;
    double cost;            /* Інтегральний ривок: ∫ ||jerk(t)||² dt */
    uint32_t iteration;     /* Номер ітерації Anytime-оптимізації */
    bool is_emergency;      /* Прапорець аварійного гальмування */
    bool is_valid;          /* Чи пройшла траєкторія перевірку колізій */
} Trajectory;

/* Допоміжні функції часу */
static inline uint64_t get_time_ns(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC_RAW, &ts);
    return (uint64_t)ts.tv_sec * 1000000000ULL + (uint64_t)ts.tv_nsec;
}

/* Обчислення квінтичного полінома та його похідних у момент часу t */
static inline Vec3 eval_poly_pos(const TrajectorySegment* seg, double t) {
    double t2 = t * t;
    double t3 = t2 * t;
    double t4 = t3 * t;
    double t5 = t4 * t;
    
    double x = seg->px.c[0] + seg->px.c[1]*t + seg->px.c[2]*t2 + seg->px.c[3]*t3 + seg->px.c[4]*t4 + seg->px.c[5]*t5;
    double y = seg->py.c[0] + seg->py.c[1]*t + seg->py.c[2]*t2 + seg->py.c[3]*t3 + seg->py.c[4]*t4 + seg->py.c[5]*t5;
    double z = seg->pz.c[0] + seg->pz.c[1]*t + seg->pz.c[2]*t2 + seg->pz.c[3]*t3 + seg->pz.c[4]*t4 + seg->pz.c[5]*t5;
    return (Vec3){x, y, z};
}

static inline Vec3 eval_poly_vel(const TrajectorySegment* seg, double t) {
    double t2 = t * t;
    double t3 = t2 * t;
    double t4 = t3 * t;
    
    double x = seg->px.c[1] + 2.0*seg->px.c[2]*t + 3.0*seg->px.c[3]*t2 + 4.0*seg->px.c[4]*t3 + 5.0*seg->px.c[5]*t4;
    double y = seg->py.c[1] + 2.0*seg->py.c[2]*t + 3.0*seg->py.c[3]*t2 + 4.0*seg->py.c[4]*t3 + 5.0*seg->py.c[5]*t4;
    double z = seg->pz.c[1] + 2.0*seg->pz.c[2]*t + 3.0*seg->pz.c[3]*t2 + 4.0*seg->pz.c[4]*t3 + 5.0*seg->pz.c[5]*t4;
    return (Vec3){x, y, z};
}

static inline Vec3 eval_poly_acc(const TrajectorySegment* seg, double t) {
    double t2 = t * t;
    double t3 = t2 * t;
    
    double x = 2.0*seg->px.c[2] + 6.0*seg->px.c[3]*t + 12.0*seg->px.c[4]*t2 + 20.0*seg->px.c[5]*t3;
    double y = 2.0*seg->py.c[2] + 6.0*seg->py.c[3]*t + 12.0*seg->py.c[4]*t2 + 20.0*seg->py.c[5]*t3;
    double z = 2.0*seg->pz.c[2] + 6.0*seg->pz.c[3]*t + 12.0*seg->pz.c[4]*t2 + 20.0*seg->pz.c[5]*t3;
    return (Vec3){x, y, z};
}

/* Розрахунок коефіцієнтів квінтичного полінома за крайовими умовами (p0, v0, a0) -> (p1, v1, a1) */
void solve_quintic_1d(double p0, double v0, double a0,
                      double p1, double v1, double a1,
                      double T, Poly1D* poly) {
    poly->c[0] = p0;
    poly->c[1] = v0;
    poly->c[2] = 0.5 * a0;
    
    double T2 = T * T;
    double T3 = T2 * T;
    double T4 = T3 * T;
    double T5 = T4 * T;
    
    double h = p1 - (p0 + v0 * T + 0.5 * a0 * T2);
    double v_diff = v1 - (v0 + a0 * T);
    double a_diff = a1 - a0;
    
    poly->c[3] = (10.0 * h - 4.0 * v_diff * T + 0.5 * a_diff * T2) / T3;
    poly->c[4] = (-15.0 * h + 7.0 * v_diff * T - a_diff * T2) / T4;
    poly->c[5] = (6.0 * h - 3.0 * v_diff * T + 0.5 * a_diff * T2) / T5;
}

/* Перевірка сегмента на перетин із перешкодами */
bool check_segment_collision(const TrajectorySegment* seg,
                             const SphereObstacle* obstacles,
                             size_t num_obs,
                             double safety_dist) {
    const int num_samples = 15;
    double dt = seg->duration / (double)num_samples;
    
    for (int i = 0; i <= num_samples; ++i) {
        double t = i * dt;
        Vec3 pos = eval_poly_pos(seg, t);
        
        for (size_t o = 0; o < num_obs; ++o) {
            Vec3 diff = vec3_sub(pos, obstacles[o].center);
            double dist = vec3_norm(diff);
            if (dist < (obstacles[o].radius + safety_dist)) {
                return false; /* Колізія */
            }
        }
    }
    return true;
}

/* Генерація примітива аварійного гальмування (Emergency Braking Primitive) */
Trajectory generate_emergency_stop_trajectory(const DroneState* start, const DroneLimits* limits) {
    Trajectory traj;
    memset(&traj, 0, sizeof(traj));
    traj.num_segments = 1;
    traj.is_emergency = true;
    
    double current_speed = vec3_norm(start->vel);
    if (current_speed < 0.05) {
        /* Дрон практично стоїть — зависання на місці */
        traj.segments[0].duration = 1.0;
        solve_quintic_1d(start->pos.x, 0, 0, start->pos.x, 0, 0, 1.0, &traj.segments[0].px);
        solve_quintic_1d(start->pos.y, 0, 0, start->pos.y, 0, 0, 1.0, &traj.segments[0].py);
        solve_quintic_1d(start->pos.z, 0, 0, start->pos.z, 0, 0, 1.0, &traj.segments[0].pz);
        traj.total_duration = 1.0;
        traj.is_valid = true;
        return traj;
    }
    
    /* Час гальмування при максимальному допустимому уповільненні */
    double decel = limits->max_acc * 0.85; /* Запас 15% на динаміку */
    double T_brake = current_speed / decel;
    if (T_brake < 0.2) T_brake = 0.2;
    
    /* Дистанція гальмування d = v * t / 2 */
    Vec3 stop_pos = vec3_add(start->pos, vec3_scale(start->vel, 0.5 * T_brake));
    
    traj.segments[0].duration = T_brake;
    solve_quintic_1d(start->pos.x, start->vel.x, start->acc.x, stop_pos.x, 0.0, 0.0, T_brake, &traj.segments[0].px);
    solve_quintic_1d(start->pos.y, start->vel.y, start->acc.y, stop_pos.y, 0.0, 0.0, T_brake, &traj.segments[0].py);
    solve_quintic_1d(start->pos.z, start->vel.z, start->acc.z, stop_pos.z, 0.0, 0.0, T_brake, &traj.segments[0].pz);
    
    traj.total_duration = T_brake;
    traj.cost = 999999.0;
    traj.is_valid = true;
    return traj;
}

/* Обчислення функції вартості (сумарний інтегральний ривок) */
double compute_trajectory_cost(const Trajectory* traj) {
    double total_cost = 0.0;
    for (size_t s = 0; s < traj->num_segments; ++s) {
        const TrajectorySegment* seg = &traj->segments[s];
        double T = seg->duration;
        /* Інтеграл від ривка квінтичного полінома: ∫_0^T (c3*6 + c4*24*t + c5*60*t²)² dt */
        double c3_sq = seg->px.c[3]*seg->px.c[3] + seg->py.c[3]*seg->py.c[3] + seg->pz.c[3]*seg->pz.c[3];
        double c4_sq = seg->px.c[4]*seg->px.c[4] + seg->py.c[4]*seg->py.c[4] + seg->pz.c[4]*seg->pz.c[4];
        double c5_sq = seg->px.c[5]*seg->px.c[5] + seg->py.c[5]*seg->py.c[5] + seg->pz.c[5]*seg->pz.c[5];
        total_cost += (36.0 * c3_sq * T + 192.0 * c4_sq * T * T * T + 720.0 * c5_sq * pow(T, 5));
    }
    return total_cost;
}

/* Головний цикл Anytime-планувальника */
Trajectory plan_anytime_trajectory(const DroneState* start_state,
                                   const Vec3* waypoints,
                                   size_t num_wp,
                                   const SphereObstacle* obstacles,
                                   size_t num_obs,
                                   const DroneLimits* limits,
                                   uint32_t budget_us) {
    uint64_t start_time = get_time_ns();
    uint64_t deadline_ns = start_time + (uint64_t)budget_us * 1000ULL;
    
    /* 1. Початковий гарантований резервний розв'язок — аварійна зупинка */
    Trajectory best_traj = generate_emergency_stop_trajectory(start_state, limits);
    
    if (num_wp < 1) {
        return best_traj;
    }
    
    /* 2. Фаза 1: Жадібна побудова початкового розв'язку (Seed Trajectory) */
    Trajectory seed_traj;
    memset(&seed_traj, 0, sizeof(seed_traj));
    seed_traj.num_segments = (num_wp < MAX_POLY_SEGMENTS) ? num_wp : MAX_POLY_SEGMENTS;
    
    DroneState curr_wp_state = *start_state;
    bool seed_valid = true;
    double current_time_alloc = 1.8; /* Базова тривалість сегмента */
    
    for (size_t s = 0; s < seed_traj.num_segments; ++s) {
        Vec3 target_p = waypoints[s];
        Vec3 target_v = (s == seed_traj.num_segments - 1) ? (Vec3){0, 0, 0} :
                        vec3_scale(vec3_sub(target_p, curr_wp_state.pos), 0.5);
        Vec3 target_a = (Vec3){0, 0, 0};
        
        seed_traj.segments[s].duration = current_time_alloc;
        solve_quintic_1d(curr_wp_state.pos.x, curr_wp_state.vel.x, curr_wp_state.acc.x,
                         target_p.x, target_v.x, target_a.x, current_time_alloc, &seed_traj.segments[s].px);
        solve_quintic_1d(curr_wp_state.pos.y, curr_wp_state.vel.y, curr_wp_state.acc.y,
                         target_p.y, target_v.y, target_a.y, current_time_alloc, &seed_traj.segments[s].py);
        solve_quintic_1d(curr_wp_state.pos.z, curr_wp_state.vel.z, curr_wp_state.acc.z,
                         target_p.z, target_v.z, target_a.z, current_time_alloc, &seed_traj.segments[s].pz);
        
        if (!check_segment_collision(&seed_traj.segments[s], obstacles, num_obs, limits->safety_dist)) {
            seed_valid = false;
            break;
        }
        
        curr_wp_state.pos = target_p;
        curr_wp_state.vel = target_v;
        curr_wp_state.acc = target_a;
    }
    
    if (seed_valid) {
        seed_traj.total_duration = current_time_alloc * (double)seed_traj.num_segments;
        seed_traj.cost = compute_trajectory_cost(&seed_traj);
        seed_traj.is_valid = true;
        seed_traj.is_emergency = false;
        seed_traj.iteration = 1;
        best_traj = seed_traj;
    }
    
    /* 3. Фаза 2 та 3: Ітеративне покращення за принципом Anytime до вичерпання кванту */
    uint32_t iteration = 1;
    while (get_time_ns() < deadline_ns) {
        iteration++;
        
        /* Спроба оптимізувати часовий розподіл та знизити ривок (Time-scaling step) */
        double step_scale = 1.0 - (0.05 * (double)(iteration % 10));
        if (step_scale < 0.4) step_scale = 0.4;
        
        Trajectory candidate = best_traj;
        candidate.iteration = iteration;
        bool cand_valid = true;
        
        curr_wp_state = *start_state;
        for (size_t s = 0; s < candidate.num_segments; ++s) {
            /* Перевірка дедлайну всередині гарячого циклу */
            if (get_time_ns() >= deadline_ns) {
                cand_valid = false;
                break;
            }
            
            Vec3 target_p = waypoints[s];
            double seg_T = current_time_alloc * step_scale;
            candidate.segments[s].duration = seg_T;
            
            Vec3 target_v = (s == candidate.num_segments - 1) ? (Vec3){0, 0, 0} :
                            vec3_scale(vec3_sub(target_p, curr_wp_state.pos), 0.6);
            Vec3 target_a = (Vec3){0, 0, 0};
            
            solve_quintic_1d(curr_wp_state.pos.x, curr_wp_state.vel.x, curr_wp_state.acc.x,
                             target_p.x, target_v.x, target_a.x, seg_T, &candidate.segments[s].px);
            solve_quintic_1d(curr_wp_state.pos.y, curr_wp_state.vel.y, curr_wp_state.acc.y,
                             target_p.y, target_v.y, target_a.y, seg_T, &candidate.segments[s].py);
            solve_quintic_1d(curr_wp_state.pos.z, curr_wp_state.vel.z, curr_wp_state.acc.z,
                             target_p.z, target_v.z, target_a.z, seg_T, &candidate.segments[s].pz);
            
            if (!check_segment_collision(&candidate.segments[s], obstacles, num_obs, limits->safety_dist)) {
                cand_valid = false;
                break;
            }
            
            curr_wp_state.pos = target_p;
            curr_wp_state.vel = target_v;
            curr_wp_state.acc = target_a;
        }
        
        if (cand_valid) {
            candidate.cost = compute_trajectory_cost(&candidate);
            /* Приймаємо, якщо вартість покращилася або ми вийшли з аварійного стану */
            if (best_traj.is_emergency || candidate.cost < best_traj.cost) {
                best_traj = candidate;
                best_traj.is_emergency = false;
                best_traj.is_valid = true;
            }
        }
    }
    
    return best_traj;
}

int main(void) {
    printf("=== Демонстрація Anytime-планувальника траєкторій (C) ===\n");
    
    DroneState start = {
        .pos = {0.0, 0.0, 2.0},
        .vel = {6.0, 1.0, 0.0}, /* Рух на швидкості 6 м/с */
        .acc = {0.0, 0.0, 0.0},
        .yaw = 0.0
    };
    
    DroneLimits limits = {
        .max_vel = 12.0,
        .max_acc = 5.0,
        .max_jerk = 20.0,
        .safety_dist = 0.4
    };
    
    Vec3 waypoints[3] = {
        {6.0, 2.0, 2.5},
        {12.0, 0.0, 2.0},
        {18.0, 4.0, 3.0}
    };
    
    SphereObstacle obstacles[2] = {
        {.center = {6.0, 0.5, 2.2}, .radius = 1.0},
        {.center = {14.0, 2.0, 2.5}, .radius = 0.8}
    };
    
    /* Тест 1: Жорсткий дедлайн 10 мс (10000 мкс) */
    uint32_t budget_us = 10000;
    uint64_t t0 = get_time_ns();
    Trajectory plan = plan_anytime_trajectory(&start, waypoints, 3, obstacles, 2, &limits, budget_us);
    uint64_t elapsed_us = (get_time_ns() - t0) / 1000ULL;
    
    printf("Бюджет: %u мкс | Витрачено: %llu мкс\n", budget_us, (unsigned long long)elapsed_us);
    printf("Статус: %s | Ітерацій: %u | Сегментів: %zu | Тривалість: %.2f с | Вартість: %.1f\n",
           plan.is_emergency ? "АВАРІЙНЕ ГАЛЬМУВАННЯ" : "УСПІШНИЙ ПЛАН",
           plan.iteration, plan.num_segments, plan.total_duration, plan.cost);
    
    /* Опитування траєкторії в t = 0.5 с */
    if (plan.is_valid && plan.num_segments > 0) {
        Vec3 p = eval_poly_pos(&plan.segments[0], 0.5);
        Vec3 v = eval_poly_vel(&plan.segments[0], 0.5);
        printf("Точка t=0.5с: Pos=[%.2f, %.2f, %.2f], Vel=[%.2f, %.2f, %.2f]\n",
               p.x, p.y, p.z, v.x, v.y, v.z);
    }
    
    return 0;
}
