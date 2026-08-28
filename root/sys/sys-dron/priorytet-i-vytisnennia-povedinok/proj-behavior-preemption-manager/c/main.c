#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <math.h>

#define BEHAVIOR_MAX_COUNT 8
#define PREEMPTION_TIMEOUT_TICKS 2

typedef enum {
    BEHAVIOR_STATE_IDLE = 0,
    BEHAVIOR_STATE_RUNNING,
    BEHAVIOR_STATE_SUSPENDED,
    BEHAVIOR_STATE_ABORTED
} behavior_state_t;

typedef enum {
    PREEMPT_REASON_NONE = 0,
    PREEMPT_REASON_COLLISION_AVOIDANCE,
    PREEMPT_REASON_CRITICAL_BATTERY,
    PREEMPT_REASON_GEOFENCE_BREACH,
    PREEMPT_REASON_MANUAL_OVERRIDE
} preempt_reason_t;

typedef struct {
    float vx;       /* м/с */
    float vy;       /* м/с */
    float vz;       /* м/с (Z вгору) */
    float yaw_rate; /* рад/с */
} motion_setpoint_t;

typedef struct {
    uint16_t waypoint_id;
    float spline_s;
    float saved_speed;
    uint32_t flags;
} checkpoint_t;

struct behavior;

typedef struct {
    bool (*init)(struct behavior *self);
    void (*tick)(struct behavior *self, float dt, motion_setpoint_t *out_sp);
    bool (*halt)(struct behavior *self, preempt_reason_t reason);
    bool (*resume)(struct behavior *self, const checkpoint_t *cp);
} behavior_vtable_t;

typedef struct behavior {
    char name[32];
    uint8_t priority;
    behavior_state_t state;
    checkpoint_t checkpoint;
    const behavior_vtable_t *vtable;
    void *ctx;
} behavior_t;

typedef struct {
    motion_setpoint_t current_sp;
    motion_setpoint_t current_accel;
    float max_accel; /* м/с² */
    float max_jerk;  /* м/с³ */
} bumpless_filter_t;

typedef struct {
    behavior_t *registry[BEHAVIOR_MAX_COUNT];
    size_t count;
    int active_idx;
    bumpless_filter_t filter;
} behavior_manager_t;

/* --- Реалізація безпоштовхового фільтра --- */
static inline float clamp_val(float v, float min_v, float max_v) {
    if (v < min_v) return min_v;
    if (v > max_v) return max_v;
    return v;
}

void bumpless_filter_init(bumpless_filter_t *f, float max_accel, float max_jerk) {
    memset(f, 0, sizeof(*f));
    f->max_accel = max_accel;
    f->max_jerk = max_jerk;
}

void bumpless_filter_update(bumpless_filter_t *f, const motion_setpoint_t *target, float dt) {
    const float kp = 2.5f;

    /* Розрахунок бажаного прискорення для компенсації розриву швидкості */
    float des_ax = clamp_val((target->vx - f->current_sp.vx) * kp, -f->max_accel, f->max_accel);
    float des_ay = clamp_val((target->vy - f->current_sp.vy) * kp, -f->max_accel, f->max_accel);
    float des_az = clamp_val((target->vz - f->current_sp.vz) * kp, -f->max_accel, f->max_accel);

    /* Обмеження ривка (похідної прискорення) */
    float jx = clamp_val((des_ax - f->current_accel.vx) / dt, -f->max_jerk, f->max_jerk);
    float jy = clamp_val((des_ay - f->current_accel.vy) / dt, -f->max_jerk, f->max_jerk);
    float jz = clamp_val((des_az - f->current_accel.vz) / dt, -f->max_jerk, f->max_jerk);

    f->current_accel.vx += jx * dt;
    f->current_accel.vy += jy * dt;
    f->current_accel.vz += jz * dt;

    f->current_sp.vx += f->current_accel.vx * dt;
    f->current_sp.vy += f->current_accel.vy * dt;
    f->current_sp.vz += f->current_accel.vz * dt;
    f->current_sp.yaw_rate = target->yaw_rate;
}

/* --- Конкретна поведінка 1: Маршрутний політ (Waypoint Cruise) --- */
typedef struct {
    uint16_t current_wp;
    float current_progress;
    float cruise_speed;
} cruise_context_t;

static bool cruise_init(behavior_t *self) {
    cruise_context_t *ctx = (cruise_context_t *)self->ctx;
    ctx->current_wp = 1;
    ctx->current_progress = 0.0f;
    ctx->cruise_speed = 15.0f;
    return true;
}

static void cruise_tick(behavior_t *self, float dt, motion_setpoint_t *out_sp) {
    cruise_context_t *ctx = (cruise_context_t *)self->ctx;
    ctx->current_progress += 0.02f * dt;
    if (ctx->current_progress >= 1.0f) {
        ctx->current_progress = 0.0f;
        ctx->current_wp++;
    }
    out_sp->vx = ctx->cruise_speed;
    out_sp->vy = 0.0f;
    out_sp->vz = 0.0f;
    out_sp->yaw_rate = 0.0f;
}

static bool cruise_halt(behavior_t *self, preempt_reason_t reason) {
    cruise_context_t *ctx = (cruise_context_t *)self->ctx;
    (void)reason;
    /* Збереження інваріантного стану місії в чекпоінт */
    self->checkpoint.waypoint_id = ctx->current_wp;
    self->checkpoint.spline_s = ctx->current_progress;
    self->checkpoint.saved_speed = ctx->cruise_speed;
    return true;
}

static bool cruise_resume(behavior_t *self, const checkpoint_t *cp) {
    cruise_context_t *ctx = (cruise_context_t *)self->ctx;
    ctx->current_wp = cp->waypoint_id;
    ctx->current_progress = cp->spline_s;
    ctx->cruise_speed = cp->saved_speed;
    return true;
}

static const behavior_vtable_t g_cruise_vtable = {
    .init = cruise_init,
    .tick = cruise_tick,
    .halt = cruise_halt,
    .resume = cruise_resume
};

/* --- Конкретна поведінка 2: Ухилення від перешкод (Collision Avoidance) --- */
typedef struct {
    bool obstacle_detected;
    float climb_rate;
    float lateral_speed;
} avoidance_context_t;

static bool avoid_init(behavior_t *self) {
    avoidance_context_t *ctx = (avoidance_context_t *)self->ctx;
    ctx->obstacle_detected = false;
    ctx->climb_rate = 3.5f;
    ctx->lateral_speed = -2.0f;
    return true;
}

static void avoid_tick(behavior_t *self, float dt, motion_setpoint_t *out_sp) {
    avoidance_context_t *ctx = (avoidance_context_t *)self->ctx;
    (void)dt;
    out_sp->vx = 0.0f;
    out_sp->vy = ctx->lateral_speed;
    out_sp->vz = ctx->climb_rate;
    out_sp->yaw_rate = 0.1f;
}

static bool avoid_halt(behavior_t *self, preempt_reason_t reason) {
    avoidance_context_t *ctx = (avoidance_context_t *)self->ctx;
    (void)reason;
    ctx->obstacle_detected = false;
    return true;
}

static bool avoid_resume(behavior_t *self, const checkpoint_t *cp) {
    (void)self;
    (void)cp;
    return true;
}

static const behavior_vtable_t g_avoid_vtable = {
    .init = avoid_init,
    .tick = avoid_tick,
    .halt = avoid_halt,
    .resume = avoid_resume
};

/* --- Менеджер поведінок --- */
void manager_init(behavior_manager_t *m, float max_accel, float max_jerk) {
    memset(m, 0, sizeof(*m));
    m->active_idx = -1;
    bumpless_filter_init(&m->filter, max_accel, max_jerk);
}

bool manager_register(behavior_manager_t *m, behavior_t *b) {
    if (m->count >= BEHAVIOR_MAX_COUNT || b == NULL) return false;
    m->registry[m->count++] = b;
    if (b->vtable && b->vtable->init) {
        b->vtable->init(b);
    }
    b->state = BEHAVIOR_STATE_IDLE;
    return true;
}

void manager_step(behavior_manager_t *m, float dt, motion_setpoint_t *final_sp) {
    int candidate_idx = -1;
    uint8_t top_prio = 0;

    /* Вибір кандидата з найвищим пріоритетом */
    for (size_t i = 0; i < m->count; ++i) {
        behavior_t *b = m->registry[i];
        if (b->state == BEHAVIOR_STATE_RUNNING || b->state == BEHAVIOR_STATE_SUSPENDED) {
            if (b->priority > top_prio) {
                top_prio = b->priority;
                candidate_idx = (int)i;
            }
        }
    }

    /* Обробка зміни активної задачі */
    if (candidate_idx != m->active_idx) {
        if (m->active_idx >= 0) {
            behavior_t *old_b = m->registry[m->active_idx];
            if (old_b->state == BEHAVIOR_STATE_RUNNING) {
                if (old_b->vtable && old_b->vtable->halt) {
                    old_b->vtable->halt(old_b, PREEMPT_REASON_COLLISION_AVOIDANCE);
                }
                old_b->state = BEHAVIOR_STATE_SUSPENDED;
            }
        }

        if (candidate_idx >= 0) {
            behavior_t *new_b = m->registry[candidate_idx];
            if (new_b->state == BEHAVIOR_STATE_SUSPENDED) {
                if (new_b->vtable && new_b->vtable->resume) {
                    new_b->vtable->resume(new_b, &new_b->checkpoint);
                }
            }
            new_b->state = BEHAVIOR_STATE_RUNNING;
        }

        m->active_idx = candidate_idx;
    }

    /* Опитування активної поведінки */
    motion_setpoint_t raw_sp = {0};
    if (m->active_idx >= 0) {
        behavior_t *active = m->registry[m->active_idx];
        if (active->vtable && active->vtable->tick) {
            active->vtable->tick(active, dt, &raw_sp);
        }
    }

    /* Безпоштовхове згладжування уставок */
    bumpless_filter_update(&m->filter, &raw_sp, dt);
    *final_sp = m->filter.current_sp;
}

/* --- Тестовий стенд імітації польоту --- */
int main(void) {
    behavior_manager_t mgr;
    manager_init(&mgr, 4.0f, 12.0f);

    cruise_context_t cruise_ctx;
    behavior_t cruise_behavior = {
        .name = "WaypointCruise",
        .priority = 40,
        .state = BEHAVIOR_STATE_IDLE,
        .vtable = &g_cruise_vtable,
        .ctx = &cruise_ctx
    };

    avoidance_context_t avoid_ctx;
    behavior_t avoid_behavior = {
        .name = "CollisionAvoidance",
        .priority = 80,
        .state = BEHAVIOR_STATE_IDLE,
        .vtable = &g_avoid_vtable,
        .ctx = &avoid_ctx
    };

    manager_register(&mgr, &cruise_behavior);
    manager_register(&mgr, &avoid_behavior);

    /* Активація круїзної місії */
    cruise_behavior.state = BEHAVIOR_STATE_RUNNING;

    const float dt = 0.02f; /* 50 Гц */
    motion_setpoint_t sp;

    printf("=== СТАРТ СИМУЛЯЦІЇ ВИТІСНЕННЯ (50 Гц) ===\n");
    for (int step = 0; step <= 250; ++step) {
        float t = step * dt;

        /* Подія 1: Виявлення перешкоди на 1.0 с */
        if (step == 50) {
            printf("\n[t=%.2f с] ПОДІЯ: Лідар зафіксував перешкоду! Активація CollisionAvoidance (Prio 80)\n", t);
            avoid_behavior.state = BEHAVIOR_STATE_RUNNING;
        }

        /* Подія 2: Перешкоду усунено на 3.0 с */
        if (step == 150) {
            printf("\n[t=%.2f с] ПОДІЯ: Перешкоду оминуто! Деактивація CollisionAvoidance\n", t);
            avoid_behavior.state = BEHAVIOR_STATE_IDLE;
        }

        manager_step(&mgr, dt, &sp);

        if (step % 25 == 0 || step == 51 || step == 151) {
            const char *active_name = (mgr.active_idx >= 0) ? mgr.registry[mgr.active_idx]->name : "NONE";
            printf("[t=%5.2f с] Активна: %-18s | vx=%6.2f | vy=%6.2f | vz=%5.2f м/с\n",
                   t, active_name, sp.vx, sp.vy, sp.vz);
        }
    }

    printf("\n=== ТЕСТ ЗАВЕРШЕНО УСПІШНО ===\n");
    return 0;
}
