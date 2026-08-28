#include <stdint.h>
#include <stdbool.h>
#include <math.h>

#define SAFETY_MARGIN_M       0.35f
#define MAX_BRAKE_ACCEL_MPS2  3.0f
#define LATENCY_PAD_SEC       0.04f
#define MAX_ALLOWED_SPEED_MPS 2.5f
#define MAX_YAW_RATE_RADPS    1.8f
#define CRITICAL_VOLTAGE_V    13.8f
#define NOMINAL_VOLTAGE_V     16.0f
#define WATCHDOG_MAX_TICKS    10

typedef struct {
    float vx;       /* Лінійна швидкість уперед, м/с */
    float vy;       /* Бічна швидкість, м/с */
    float yaw_rate; /* Кутова швидкість рискання, рад/с */
} CommandVector;

typedef struct {
    float obstacle_dist_m; /* Найменша відстань за променем руху, м */
    float battery_voltage; /* Напруга силової шини, В */
    float current_tilt_rad;/* Поточний кут відхилення від вертикалі, рад */
    float max_tilt_limit;  /* Критичний кут нахилу, рад */
    bool  emergency_switch;/* Апаратна кнопка аварійної зупинки */
} SensorEnvelope;

typedef enum {
    SAFETY_PASS_THROUGH = 0,
    SAFETY_CLAMPED      = 1,
    SAFETY_BRAKE_ENGAGED= 2,
    SAFETY_ESTOP_ACTIVE = 3
} SafetyStatus;

typedef struct {
    uint32_t last_valid_tick;
    uint32_t current_tick;
    float    last_safe_vx;
} SafetySupervisorState;

void safety_supervisor_init(SafetySupervisorState *state) {
    if (!state) return;
    state->last_valid_tick = 0;
    state->current_tick = 0;
    state->last_safe_vx = 0.0f;
}

SafetyStatus safety_filter_step(
    SafetySupervisorState *state,
    const CommandVector *candidate,
    const SensorEnvelope *sensors,
    float dt_sec,
    CommandVector *out_safe_cmd
) {
    if (!state || !candidate || !sensors || !out_safe_cmd || dt_sec <= 0.0f) {
        return SAFETY_ESTOP_ACTIVE;
    }

    state->current_tick++;

    /* 1. Апаратний аварійний вимикач має найвищий пріоритет */
    if (sensors->emergency_switch) {
        out_safe_cmd->vx = 0.0f;
        out_safe_cmd->vy = 0.0f;
        out_safe_cmd->yaw_rate = 0.0f;
        state->last_safe_vx = 0.0f;
        return SAFETY_ESTOP_ACTIVE;
    }

    /* 2. Перевірка сторожового таймера оптимізатора */
    if ((state->current_tick - state->last_valid_tick) > WATCHDOG_MAX_TICKS) {
        /* Плавне гальмування до нуля */
        float decel = MAX_BRAKE_ACCEL_MPS2 * dt_sec;
        if (state->last_safe_vx > decel) {
            state->last_safe_vx -= decel;
        } else {
            state->last_safe_vx = 0.0f;
        }
        out_safe_cmd->vx = state->last_safe_vx;
        out_safe_cmd->vy = 0.0f;
        out_safe_cmd->yaw_rate = 0.0f;
        return SAFETY_BRAKE_ENGAGED;
    }

    /* 3. Розрахунок гальмівного бар'єра за дистанцією */
    float target_vx = candidate->vx;
    if (target_vx < 0.0f) {
        target_vx = 0.0f; /* Заборона руху назад у спрощеній моделі */
    }

    float stop_dist = (target_vx * target_vx) / (2.0f * MAX_BRAKE_ACCEL_MPS2)
                    + target_vx * LATENCY_PAD_SEC
                    + SAFETY_MARGIN_M;

    bool clamped = false;

    if (sensors->obstacle_dist_m < stop_dist) {
        /* Допустима швидкість із залишком безпечної дистанції */
        float available_dist = sensors->obstacle_dist_m - SAFETY_MARGIN_M;
        if (available_dist <= 0.05f) {
            target_vx = 0.0f;
        } else {
            float max_v_safe = sqrtf(2.0f * MAX_BRAKE_ACCEL_MPS2 * available_dist);
            if (target_vx > max_v_safe) {
                target_vx = max_v_safe;
                clamped = true;
            }
        }
    }

    /* 4. Масштабування за напругою акумулятора */
    if (sensors->battery_voltage < NOMINAL_VOLTAGE_V) {
        float v_factor = (sensors->battery_voltage - CRITICAL_VOLTAGE_V)
                       / (NOMINAL_VOLTAGE_V - CRITICAL_VOLTAGE_V);
        if (v_factor < 0.0f) v_factor = 0.0f;
        if (v_factor > 1.0f) v_factor = 1.0f;

        float max_bat_vx = MAX_ALLOWED_SPEED_MPS * v_factor;
        if (target_vx > max_bat_vx) {
            target_vx = max_bat_vx;
            clamped = true;
        }
    }

    /* 5. Захист від перевертання за кутом нахилу */
    float target_yaw_rate = candidate->yaw_rate;
    if (sensors->current_tilt_rad > (sensors->max_tilt_limit * 0.8f)) {
        float tilt_scale = (sensors->max_tilt_limit - sensors->current_tilt_rad)
                         / (sensors->max_tilt_limit * 0.2f);
        if (tilt_scale < 0.0f) tilt_scale = 0.0f;
        if (tilt_scale > 1.0f) tilt_scale = 1.0f;

        target_yaw_rate *= tilt_scale;
        target_vx *= tilt_scale;
        clamped = true;
    }

    /* 6. Обмеження абсолютних меж швидкості */
    if (target_vx > MAX_ALLOWED_SPEED_MPS) {
        target_vx = MAX_ALLOWED_SPEED_MPS;
        clamped = true;
    }
    if (target_yaw_rate > MAX_YAW_RATE_RADPS) {
        target_yaw_rate = MAX_YAW_RATE_RADPS;
        clamped = true;
    } else if (target_yaw_rate < -MAX_YAW_RATE_RADPS) {
        target_yaw_rate = -MAX_YAW_RATE_RADPS;
        clamped = true;
    }

    out_safe_cmd->vx = target_vx;
    out_safe_cmd->vy = candidate->vy; /* Бічна швидкість для ровера = 0 */
    out_safe_cmd->yaw_rate = target_yaw_rate;

    state->last_safe_vx = target_vx;
    state->last_valid_tick = state->current_tick;

    return clamped ? SAFETY_CLAMPED : SAFETY_PASS_THROUGH;
}
