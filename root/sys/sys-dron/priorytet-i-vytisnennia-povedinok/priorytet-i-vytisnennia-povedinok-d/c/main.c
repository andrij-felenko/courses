#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define BEHAVIOR_MAX_COUNT 8
#define PREEMPTION_TIMEOUT_CYCLES 2

typedef enum {
    BEHAVIOR_STATE_INACTIVE = 0,
    BEHAVIOR_STATE_RUNNING,
    BEHAVIOR_STATE_SUSPENDED,
    BEHAVIOR_STATE_FAILED
} behavior_state_t;

typedef enum {
    PREEMPT_REASON_NONE = 0,
    PREEMPT_REASON_SAFETY_OVERRIDE,
    PREEMPT_REASON_FAILSAFE,
    PREEMPT_REASON_OPERATOR_ABORT
} preempt_reason_t;

typedef struct {
    float vx;       /* м/с */
    float vy;       /* м/с */
    float vz;       /* м/с */
    float yaw_rate; /* рад/с */
} motion_setpoint_t;

typedef struct {
    uint16_t waypoint_index;
    float spline_progress;
    uint32_t survey_grid_mask;
    float accumulated_energy_mah;
} behavior_checkpoint_t;

struct behavior;

typedef struct {
    bool (*init)(struct behavior *self);
    void (*update)(struct behavior *self, float dt, motion_setpoint_t *out_sp);
    bool (*halt)(struct behavior *self, preempt_reason_t reason);
    bool (*resume)(struct behavior *self, const behavior_checkpoint_t *cp);
} behavior_ops_t;

typedef struct behavior {
    const char *name;
    uint8_t priority;
    behavior_state_t state;
    behavior_checkpoint_t checkpoint;
    const behavior_ops_t *ops;
    void *user_data;
} behavior_t;

typedef struct {
    behavior_t *behaviors[BEHAVIOR_MAX_COUNT];
    size_t count;
    int8_t active_index;
    motion_setpoint_t current_smoothed_sp;
    motion_setpoint_t current_accel;
    float max_accel; /* м/с² */
    float max_jerk;  /* м/с³ */
} behavior_dispatcher_t;

static inline float clamp_float(float val, float min_val, float max_val) {
    if (val < min_val) return min_val;
    if (val > max_val) return max_val;
    return val;
}

void dispatcher_init(behavior_dispatcher_t *d, float max_accel, float max_jerk) {
    memset(d, 0, sizeof(*d));
    d->active_index = -1;
    d->max_accel = max_accel;
    d->max_jerk = max_jerk;
}

bool dispatcher_register(behavior_dispatcher_t *d, behavior_t *b) {
    if (d->count >= BEHAVIOR_MAX_COUNT || b == NULL) return false;
    d->behaviors[d->count++] = b;
    if (b->ops && b->ops->init) {
        b->ops->init(b);
    }
    b->state = BEHAVIOR_STATE_INACTIVE;
    return true;
}

static void apply_bumpless_filter(behavior_dispatcher_t *d, const motion_setpoint_t *target, float dt) {
    const float kp = 2.5f;

    /* Розрахунок бажаного прискорення для компенсації розриву швидкості */
    float des_ax = clamp_float((target->vx - d->current_smoothed_sp.vx) * kp, -d->max_accel, d->max_accel);
    float des_ay = clamp_float((target->vy - d->current_smoothed_sp.vy) * kp, -d->max_accel, d->max_accel);
    float des_az = clamp_float((target->vz - d->current_smoothed_sp.vz) * kp, -d->max_accel, d->max_accel);

    /* Обмеження ривка */
    float jx = clamp_float((des_ax - d->current_accel.vx) / dt, -d->max_jerk, d->max_jerk);
    float jy = clamp_float((des_ay - d->current_accel.vy) / dt, -d->max_jerk, d->max_jerk);
    float jz = clamp_float((des_az - d->current_accel.vz) / dt, -d->max_jerk, d->max_jerk);

    d->current_accel.vx += jx * dt;
    d->current_accel.vy += jy * dt;
    d->current_accel.vz += jz * dt;

    d->current_smoothed_sp.vx += d->current_accel.vx * dt;
    d->current_smoothed_sp.vy += d->current_accel.vy * dt;
    d->current_smoothed_sp.vz += d->current_accel.vz * dt;
    d->current_smoothed_sp.yaw_rate = target->yaw_rate;
}

void dispatcher_tick(behavior_dispatcher_t *d, float dt, motion_setpoint_t *out_sp) {
    int8_t best_candidate = -1;
    uint8_t highest_prio = 0;

    /* Пошук найвищої за пріоритетом активної або призупиненої поведінки */
    for (size_t i = 0; i < d->count; ++i) {
        behavior_t *b = d->behaviors[i];
        if (b->state == BEHAVIOR_STATE_RUNNING || b->state == BEHAVIOR_STATE_SUSPENDED) {
            if (b->priority > highest_prio) {
                highest_prio = b->priority;
                best_candidate = (int8_t)i;
            }
        }
    }

    /* Обробка зміни активної поведінки та виклику halt / resume */
    if (best_candidate != d->active_index) {
        if (d->active_index >= 0) {
            behavior_t *current = d->behaviors[d->active_index];
            if (current->state == BEHAVIOR_STATE_RUNNING) {
                if (current->ops && current->ops->halt) {
                    current->ops->halt(current, PREEMPT_REASON_SAFETY_OVERRIDE);
                }
                current->state = BEHAVIOR_STATE_SUSPENDED;
            }
        }

        if (best_candidate >= 0) {
            behavior_t *next = d->behaviors[best_candidate];
            if (next->state == BEHAVIOR_STATE_SUSPENDED && next->ops && next->ops->resume) {
                next->ops->resume(next, &next->checkpoint);
            }
            next->state = BEHAVIOR_STATE_RUNNING;
        }

        d->active_index = best_candidate;
    }

    /* Опитування активної поведінки */
    motion_setpoint_t raw_sp = {0};
    if (d->active_index >= 0) {
        behavior_t *active = d->behaviors[d->active_index];
        if (active->ops && active->ops->update) {
            active->ops->update(active, dt, &raw_sp);
        }
    }

    /* Безпоштовхова фільтрація вихідних уставок */
    apply_bumpless_filter(d, &raw_sp, dt);
    *out_sp = d->current_smoothed_sp;
}
