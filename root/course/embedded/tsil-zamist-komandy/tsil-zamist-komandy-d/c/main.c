#include <stdint.h>
#include <stdbool.h>
#include <math.h>

#define MAX_GOALS_QUEUE 8

typedef enum {
    GOAL_TYPE_WAYPOINT = 0,
    GOAL_TYPE_SURVEY_AREA,
    GOAL_TYPE_HOLD_POSITION,
    GOAL_TYPE_EMERGENCY_RTH
} GoalType_e;

typedef enum {
    GOAL_STATE_IDLE = 0,
    GOAL_STATE_PENDING,
    GOAL_STATE_ACTIVE,
    GOAL_STATE_PREEMPTED,
    GOAL_STATE_COMPLETED,
    GOAL_STATE_ABORTED,
    GOAL_STATE_REJECTED
} GoalState_e;

typedef struct {
    uint32_t id;
    GoalType_e type;
    uint8_t priority;       /* 0 (найнижчий) .. 255 (найвищий) */
    float target_x;         /* метри, світова система NED */
    float target_y;
    float target_z;
    float acceptance_radius;/* радіус зарахування точки, метри */
    float timeout_sec;      /* максимальний час виконання */
} Goal_t;

typedef struct {
    float pos_x;
    float pos_y;
    float pos_z;
    float battery_voltage;
    bool is_geofence_ok;
    bool is_ekf_healthy;
} SystemState_t;

typedef struct {
    Goal_t queue[MAX_GOALS_QUEUE];
    GoalState_e states[MAX_GOALS_QUEUE];
    uint8_t count;
    int8_t active_index;
    float active_elapsed_time;
} GoalDispatcher_t;

void dispatcher_init(GoalDispatcher_t *disp) {
    disp->count = 0;
    disp->active_index = -1;
    disp->active_elapsed_time = 0.0f;
    for (uint8_t i = 0; i < MAX_GOALS_QUEUE; i++) {
        disp->states[i] = GOAL_STATE_IDLE;
    }
}

bool dispatcher_push_goal(GoalDispatcher_t *disp, const Goal_t *new_goal) {
    if (disp->count >= MAX_GOALS_QUEUE) {
        return false; /* Черга переповнена */
    }
    disp->queue[disp->count] = *new_goal;
    disp->states[disp->count] = GOAL_STATE_PENDING;
    disp->count++;
    return true;
}

static bool validate_goal(const Goal_t *g, const SystemState_t *sys) {
    if (!sys->is_ekf_healthy || !sys->is_geofence_ok) {
        return false;
    }
    /* Для звичайних місій вимагаємо напругу не менше 21.0 В */
    if (g->type != GOAL_TYPE_EMERGENCY_RTH && sys->battery_voltage < 21.0f) {
        return false;
    }
    return true;
}

void dispatcher_tick(GoalDispatcher_t *disp, const SystemState_t *sys, float dt_sec) {
    /* 1. Пошук найпріоритетнішої цілі серед PENDING або поточної ACTIVE */
    int8_t best_index = -1;
    uint8_t highest_priority = 0;

    if (disp->active_index >= 0) {
        highest_priority = disp->queue[disp->active_index].priority;
        best_index = disp->active_index;
    }

    for (uint8_t i = 0; i < disp->count; i++) {
        if (disp->states[i] == GOAL_STATE_PENDING) {
            if (disp->active_index < 0 || disp->queue[i].priority > highest_priority) {
                highest_priority = disp->queue[i].priority;
                best_index = (int8_t)i;
            }
        }
    }

    /* 2. Обробка витіснення (Preemption), якщо знайдено більш пріоритетну ціль */
    if (best_index >= 0 && best_index != disp->active_index) {
        if (disp->active_index >= 0) {
            disp->states[disp->active_index] = GOAL_STATE_PREEMPTED;
        }
        
        if (validate_goal(&disp->queue[best_index], sys)) {
            disp->active_index = best_index;
            disp->states[best_index] = GOAL_STATE_ACTIVE;
            disp->active_elapsed_time = 0.0f;
        } else {
            disp->states[best_index] = GOAL_STATE_REJECTED;
            disp->active_index = -1;
            return;
        }
    }

    /* 3. Оновлення поточної активної цілі */
    if (disp->active_index >= 0) {
        Goal_t *cur = &disp->queue[disp->active_index];
        disp->active_elapsed_time += dt_sec;

        /* Перевірка таймауту */
        if (cur->timeout_sec > 0.0f && disp->active_elapsed_time > cur->timeout_sec) {
            disp->states[disp->active_index] = GOAL_STATE_ABORTED;
            disp->active_index = -1;
            return;
        }

        /* Розрахунок дистанції до точки */
        float dx = cur->target_x - sys->pos_x;
        float dy = cur->target_y - sys->pos_y;
        float dz = cur->target_z - sys->pos_z;
        float dist = sqrtf(dx * dx + dy * dy + dz * dz);

        if (dist <= cur->acceptance_radius) {
            disp->states[disp->active_index] = GOAL_STATE_COMPLETED;
            disp->active_index = -1;
        }
    }
}
