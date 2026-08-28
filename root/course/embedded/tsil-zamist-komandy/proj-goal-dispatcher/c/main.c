#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <math.h>

#define MAX_GOALS 8

typedef enum {
    GOAL_NAVIGATE_WAYPOINT = 0,
    GOAL_SURVEY_POLYGON,
    GOAL_LOITER_POSITION,
    GOAL_EMERGENCY_RETURN
} GoalAction_e;

typedef enum {
    STATE_EMPTY = 0,
    STATE_PENDING,
    STATE_ACTIVE,
    STATE_PREEMPTED,
    STATE_COMPLETED,
    STATE_ABORTED,
    STATE_REJECTED
} GoalState_e;

typedef struct {
    uint32_t id;
    GoalAction_e action;
    uint8_t priority;       /* 0..255 */
    float target_x;         /* метри у світовій системі NED */
    float target_y;
    float target_z;
    float tolerance_m;      /* радіус досягнення */
    float timeout_s;        /* ліміт часу на виконання */
} GoalItem_t;

typedef struct {
    float pos_x;
    float pos_y;
    float pos_z;
    float battery_v;
    bool geofence_valid;
    bool ekf_healthy;
    bool obstacle_detected;
} VehicleTelemetry_t;

typedef struct {
    GoalItem_t items[MAX_GOALS];
    GoalState_e states[MAX_GOALS];
    uint8_t count;
    int8_t active_idx;
    float active_timer_s;
} MissionDispatcher_t;

void mission_dispatcher_init(MissionDispatcher_t *disp) {
    disp->count = 0;
    disp->active_idx = -1;
    disp->active_timer_s = 0.0f;
    for (uint8_t i = 0; i < MAX_GOALS; i++) {
        disp->states[i] = STATE_EMPTY;
    }
}

bool mission_dispatcher_enqueue(MissionDispatcher_t *disp, const GoalItem_t *item) {
    if (disp->count >= MAX_GOALS) {
        return false;
    }
    disp->items[disp->count] = *item;
    disp->states[disp->count] = STATE_PENDING;
    disp->count++;
    return true;
}

static bool check_preconditions(const GoalItem_t *item, const VehicleTelemetry_t *telem) {
    if (!telem->ekf_healthy || !telem->geofence_valid) {
        return false;
    }
    if (item->action != GOAL_EMERGENCY_RETURN && telem->battery_v < 21.0f) {
        return false;
    }
    return true;
}

void mission_dispatcher_step(MissionDispatcher_t *disp, const VehicleTelemetry_t *telem, float dt_s) {
    /* 1. Якщо виявлено небезпечну перешкоду, формуємо екстрене повернення/зависання */
    if (telem->obstacle_detected && (disp->active_idx >= 0)) {
        if (disp->items[disp->active_idx].action != GOAL_EMERGENCY_RETURN) {
            GoalItem_t emergency_goal = {
                .id = 9999,
                .action = GOAL_EMERGENCY_RETURN,
                .priority = 255,
                .target_x = 0.0f,
                .target_y = 0.0f,
                .target_z = -30.0f,
                .tolerance_m = 2.0f,
                .timeout_s = 120.0f
            };
            mission_dispatcher_enqueue(disp, &emergency_goal);
        }
    }

    /* 2. Пошук найвищого пріоритету серед PENDING та поточної ACTIVE */
    int8_t candidate_idx = -1;
    uint8_t highest_prio = 0;

    if (disp->active_idx >= 0) {
        highest_prio = disp->items[disp->active_idx].priority;
        candidate_idx = disp->active_idx;
    }

    for (uint8_t i = 0; i < disp->count; i++) {
        if (disp->states[i] == STATE_PENDING) {
            if (disp->active_idx < 0 || disp->items[i].priority > highest_prio) {
                highest_prio = disp->items[i].priority;
                candidate_idx = (int8_t)i;
            }
        }
    }

    /* 3. Витіснення або перехід до нового завдання */
    if (candidate_idx >= 0 && candidate_idx != disp->active_idx) {
        if (disp->active_idx >= 0) {
            disp->states[disp->active_idx] = STATE_PREEMPTED;
            printf("[DISPATCHER] Goal #%u PREEMPTED by higher priority goal #%u\n",
                   disp->items[disp->active_idx].id, disp->items[candidate_idx].id);
        }

        if (check_preconditions(&disp->items[candidate_idx], telem)) {
            disp->active_idx = candidate_idx;
            disp->states[candidate_idx] = STATE_ACTIVE;
            disp->active_timer_s = 0.0f;
            printf("[DISPATCHER] Goal #%u ACTIVE (Priority: %u, Target: [%.1f, %.1f, %.1f])\n",
                   disp->items[candidate_idx].id,
                   disp->items[candidate_idx].priority,
                   disp->items[candidate_idx].target_x,
                   disp->items[candidate_idx].target_y,
                   disp->items[candidate_idx].target_z);
        } else {
            disp->states[candidate_idx] = STATE_REJECTED;
            printf("[DISPATCHER] Goal #%u REJECTED by pre-condition check\n",
                   disp->items[candidate_idx].id);
            disp->active_idx = -1;
            return;
        }
    }

    /* 4. Оновлення та перевірка досягнення активної мети */
    if (disp->active_idx >= 0) {
        GoalItem_t *active_goal = &disp->items[disp->active_idx];
        disp->active_timer_s += dt_s;

        /* Перевірка таймауту */
        if (active_goal->timeout_s > 0.0f && disp->active_timer_s > active_goal->timeout_s) {
            disp->states[disp->active_idx] = STATE_ABORTED;
            printf("[DISPATCHER] Goal #%u ABORTED due to timeout (%.1f s)\n",
                   active_goal->id, disp->active_timer_s);
            disp->active_idx = -1;
            return;
        }

        /* Обчислення евклідової дистанції до цільової точки */
        float dx = active_goal->target_x - telem->pos_x;
        float dy = active_goal->target_y - telem->pos_y;
        float dz = active_goal->target_z - telem->pos_z;
        float distance = sqrtf(dx * dx + dy * dy + dz * dz);

        if (distance <= active_goal->tolerance_m) {
            disp->states[disp->active_idx] = STATE_COMPLETED;
            printf("[DISPATCHER] Goal #%u COMPLETED successfully (Distance: %.2f m)\n",
                   active_goal->id, distance);
            disp->active_idx = -1;
        }
    }
}

int main(void) {
    MissionDispatcher_t dispatcher;
    mission_dispatcher_init(&dispatcher);

    VehicleTelemetry_t telemetry = {
        .pos_x = 0.0f,
        .pos_y = 0.0f,
        .pos_z = -10.0f,
        .battery_v = 24.2f,
        .geofence_valid = true,
        .ekf_healthy = true,
        .obstacle_detected = false
    };

    GoalItem_t survey_goal = {
        .id = 101,
        .action = GOAL_SURVEY_POLYGON,
        .priority = 50,
        .target_x = 100.0f,
        .target_y = 50.0f,
        .target_z = -50.0f,
        .tolerance_m = 3.0f,
        .timeout_s = 60.0f
    };

    mission_dispatcher_enqueue(&dispatcher, &survey_goal);

    printf("=== СИМУЛЯЦІЯ АВТОНОМНОГО ДИСПЕТЧЕРА ===\n");
    float dt = 1.0f;

    for (int step = 0; step < 10; step++) {
        /* Імітуємо рух до цілі */
        telemetry.pos_x += 10.0f;
        telemetry.pos_y += 5.0f;
        telemetry.pos_z -= 4.0f;

        /* На 4-му кроці раптово виявляється перешкода */
        if (step == 3) {
            printf("\n--- ПОДІЯ: Сенсор виявив перешкоду на курсі! ---\n");
            telemetry.obstacle_detected = true;
        }

        mission_dispatcher_step(&dispatcher, &telemetry, dt);
    }

    return 0;
}
