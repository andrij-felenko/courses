#ifndef GOAL_TYPES_H
#define GOAL_TYPES_H

#include <math.h>
#include <stdbool.h>
#include <stdint.h>

/* Скільки цілей уміщає бортова черга. Пам'ять під неї відводить компонувальник:
   купи на борту немає взагалі, тож немає й пауз менеджера пам'яті. */
#define MAX_GOALS 8

/* Нижня межа напруги акумулятора: під нею дозволено лише повернення додому. */
#define BATTERY_MIN_V 21.0f

/* Гістерезис витіснення. Нова ціль мусить бути щонайменше на стільки
   пріоритетнішою за активну, інакше два сусідні за вагою завдання
   перекидатимуть керування одне одному кожен такт. */
#define PREEMPT_HYSTERESIS 5

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

/* Незмінний дескриптор цілі: диспетчер його лише читає. */
typedef struct {
    uint32_t id;
    GoalAction_e action;
    uint8_t priority;   /* 0..255 */
    float target_x;     /* метри у світовій системі NED */
    float target_y;
    float target_z;
    float tolerance_m;  /* радіус, у якому ціль вважається досягнутою */
    float timeout_s;    /* ліміт часу на виконання; 0 — без ліміту */
} GoalItem_t;

/* Миттєвий зріз стану апарата: навігаційний фільтр, контролер батареї,
   далекоміри. Диспетчер його теж лише читає. */
typedef struct {
    float pos_x;
    float pos_y;
    float pos_z;
    float battery_v;
    bool geofence_valid;
    bool ekf_healthy;
    bool obstacle_detected;
} VehicleTelemetry_t;

/* Що диспетчер віддає планувальнику траєкторії цього такту. */
typedef enum {
    OUTPUT_IDLE = 0,   /* активної цілі немає — тримати позицію */
    OUTPUT_TRACK,      /* вести апарат у точку setpoint */
    OUTPUT_HOLD,       /* аварійне зависання: навігація недостовірна */
    OUTPUT_LAND        /* посадка на місці: навігації немає й батарея на межі */
} OutputMode_e;

typedef struct {
    OutputMode_e mode;
    uint32_t goal_id;  /* 0, коли активної цілі немає */
    float x;
    float y;
    float z;
} DispatcherOutput_t;

/* Стани, з яких ціль уже не повернеться в роботу. */
static inline bool goal_state_is_terminal(GoalState_e state) {
    return state == STATE_COMPLETED || state == STATE_ABORTED || state == STATE_REJECTED;
}

/* Евклідова відстань між двома точками у світовій системі. */
static inline float goal_distance(float ax, float ay, float az,
                                  float bx, float by, float bz) {
    const float dx = ax - bx;
    const float dy = ay - by;
    const float dz = az - bz;
    return sqrtf(dx * dx + dy * dy + dz * dz);
}

#endif /* GOAL_TYPES_H */
