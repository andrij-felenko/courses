#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define ARBITER_MAX_SOURCES 8
#define ARBITER_DEADTIME_MS 250

typedef enum {
    PRIORITY_AUTOMATION  = 0,
    PRIORITY_MANUAL      = 1,
    PRIORITY_PROTECTION  = 2,
    PRIORITY_SAFETY      = 3
} PriorityLevel;

typedef enum {
    ACTUATOR_CMD_STOP    = 0,
    ACTUATOR_CMD_FORWARD = 1,
    ACTUATOR_CMD_REVERSE = 2
} DiscreteCommand;

typedef enum {
    ARB_REASON_NONE             = 0,
    ARB_REASON_NORMAL_AUTO      = 1,
    ARB_REASON_MANUAL_OVERRIDE  = 2,
    ARB_REASON_PROTECTION_TRIP  = 3,
    ARB_REASON_SAFETY_SHUTDOWN  = 4,
    ARB_REASON_DEADTIME_HOLD    = 5
} ArbitrationReason;

typedef struct {
    uint8_t source_id;
    PriorityLevel priority;
    DiscreteCommand discrete_cmd;
    float analog_setpoint; // 0.0f .. 1.0f
    uint32_t timestamp_ms;
    uint32_t ttl_ms;
    bool is_active;
} ActuatorRequest;

typedef struct {
    DiscreteCommand current_discrete;
    DiscreteCommand pending_discrete;
    float current_analog;
    uint32_t deadtime_timer_ms;
    bool in_deadtime;
    uint8_t winning_source_id;
    ArbitrationReason active_reason;
    ActuatorRequest requests[ARBITER_MAX_SOURCES];
    size_t request_count;
} ActuatorArbiter;

static inline float clamp_float(float v, float min_v, float max_v) {
    if (v < min_v) return min_v;
    if (v > max_v) return max_v;
    return v;
}

void arbiter_init(ActuatorArbiter *arb) {
    if (!arb) return;
    arb->current_discrete = ACTUATOR_CMD_STOP;
    arb->pending_discrete = ACTUATOR_CMD_STOP;
    arb->current_analog = 0.0f;
    arb->deadtime_timer_ms = 0;
    arb->in_deadtime = false;
    arb->winning_source_id = 0;
    arb->active_reason = ARB_REASON_NONE;
    arb->request_count = 0;

    for (size_t i = 0; i < ARBITER_MAX_SOURCES; ++i) {
        arb->requests[i].is_active = false;
    }
}

bool arbiter_submit_request(ActuatorArbiter *arb,
                            uint8_t source_id,
                            PriorityLevel priority,
                            DiscreteCommand discrete_cmd,
                            float analog_setpoint,
                            uint32_t now_ms,
                            uint32_t ttl_ms) {
    if (!arb) return false;

    // Пошук наявного слота для цього source_id або вільного слота
    int target_slot = -1;
    for (size_t i = 0; i < arb->request_count; ++i) {
        if (arb->requests[i].source_id == source_id) {
            target_slot = (int)i;
            break;
        }
    }

    if (target_slot < 0) {
        if (arb->request_count >= ARBITER_MAX_SOURCES) return false;
        target_slot = (int)(arb->request_count++);
    }

    arb->requests[target_slot].source_id = source_id;
    arb->requests[target_slot].priority = priority;
    arb->requests[target_slot].discrete_cmd = discrete_cmd;
    arb->requests[target_slot].analog_setpoint = clamp_float(analog_setpoint, 0.0f, 1.0f);
    arb->requests[target_slot].timestamp_ms = now_ms;
    arb->requests[target_slot].ttl_ms = ttl_ms;
    arb->requests[target_slot].is_active = true;

    return true;
}

void arbiter_update(ActuatorArbiter *arb, uint32_t now_ms, uint32_t dt_ms) {
    if (!arb) return;

    // Крок 1: Інвалідація запитів за таймаутом TTL
    for (size_t i = 0; i < arb->request_count; ++i) {
        if (!arb->requests[i].is_active) continue;

        if (now_ms - arb->requests[i].timestamp_ms > arb->requests[i].ttl_ms) {
            arb->requests[i].is_active = false;
        }
    }

    // Крок 2: Пошук активного запиту з найвищим пріоритетом
    int best_slot = -1;
    PriorityLevel highest_prio = PRIORITY_AUTOMATION;

    for (size_t i = 0; i < arb->request_count; ++i) {
        if (!arb->requests[i].is_active) continue;

        if (best_slot < 0 || arb->requests[i].priority > highest_prio) {
            highest_prio = arb->requests[i].priority;
            best_slot = (int)i;
        }
    }

    DiscreteCommand target_discrete = ACTUATOR_CMD_STOP;
    float target_analog = 0.0f;
    ArbitrationReason target_reason = ARB_REASON_NONE;

    if (best_slot >= 0) {
        target_discrete = arb->requests[best_slot].discrete_cmd;
        target_analog = arb->requests[best_slot].analog_setpoint;
        arb->winning_source_id = arb->requests[best_slot].source_id;

        switch (highest_prio) {
            case PRIORITY_SAFETY:     target_reason = ARB_REASON_SAFETY_SHUTDOWN; break;
            case PRIORITY_PROTECTION: target_reason = ARB_REASON_PROTECTION_TRIP; break;
            case PRIORITY_MANUAL:     target_reason = ARB_REASON_MANUAL_OVERRIDE; break;
            default:                  target_reason = ARB_REASON_NORMAL_AUTO;     break;
        }
    } else {
        arb->winning_source_id = 0;
        target_reason = ARB_REASON_NONE;
    }

    // Крок 3: Обробка взаємного блокування та Dead-Time для реверсу
    if (arb->in_deadtime) {
        if (arb->deadtime_timer_ms <= dt_ms) {
            arb->in_deadtime = false;
            arb->deadtime_timer_ms = 0;
            arb->current_discrete = arb->pending_discrete;
            arb->active_reason = target_reason;
        } else {
            arb->deadtime_timer_ms -= dt_ms;
            arb->current_discrete = ACTUATOR_CMD_STOP;
            arb->active_reason = ARB_REASON_DEADTIME_HOLD;
        }
    } else {
        // Перевірка на зміну напрямку руху (реверс вимагає паузи)
        bool is_reversal = (arb->current_discrete == ACTUATOR_CMD_FORWARD && target_discrete == ACTUATOR_CMD_REVERSE) ||
                           (arb->current_discrete == ACTUATOR_CMD_REVERSE && target_discrete == ACTUATOR_CMD_FORWARD);

        if (is_reversal) {
            arb->in_deadtime = true;
            arb->deadtime_timer_ms = ARBITER_DEADTIME_MS;
            arb->pending_discrete = target_discrete;
            arb->current_discrete = ACTUATOR_CMD_STOP;
            arb->active_reason = ARB_REASON_DEADTIME_HOLD;
        } else {
            arb->current_discrete = target_discrete;
            arb->active_reason = target_reason;
        }
    }

    // Крок 4: Формування аналогового виходу (скидання в нуль при зупинці)
    if (arb->current_discrete == ACTUATOR_CMD_STOP) {
        arb->current_analog = 0.0f;
    } else {
        arb->current_analog = target_analog;
    }
}

DiscreteCommand arbiter_get_discrete(const ActuatorArbiter *arb) {
    return arb ? arb->current_discrete : ACTUATOR_CMD_STOP;
}

float arbiter_get_analog(const ActuatorArbiter *arb) {
    return arb ? arb->current_analog : 0.0f;
}

ArbitrationReason arbiter_get_reason(const ActuatorArbiter *arb) {
    return arb ? arb->active_reason : ARB_REASON_NONE;
}
