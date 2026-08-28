#include <stdint.h>
#include <stdbool.h>
#include <math.h>

#define MAX_CLASSES 8
#define WINDOW_SIZE 5
#define RECOVERY_TICKS 50

typedef enum {
    SUPERVISOR_STATE_NOMINAL_ML,
    SUPERVISOR_STATE_DEGRADED_HOLD,
    SUPERVISOR_STATE_RULE_FALLBACK,
    SUPERVISOR_STATE_EMERGENCY_SAFE
} supervisor_state_t;

typedef struct {
    float max_allowed_entropy;
    float min_confidence_threshold;
    uint32_t deadline_timeout_ms;
    uint8_t fault_threshold_n;
    float max_slew_rate_deg_per_s;
    float loop_dt_s;
    float kp;
    float ki;
    float kd;
} supervisor_config_t;

typedef struct {
    float u_cmd;
    float confidence;
    float class_probs[MAX_CLASSES];
    uint8_t num_classes;
    uint32_t timestamp_ms;
    bool is_fresh;
} ml_inference_frame_t;

typedef struct {
    float current_state;
    float target_state;
    float current_rate;
} plant_feedback_t;

typedef struct {
    supervisor_config_t cfg;
    supervisor_state_t state;
    uint32_t last_valid_frame_ms;
    uint8_t fault_history[WINDOW_SIZE];
    uint8_t fault_history_idx;
    uint16_t recovery_counter;
    
    /* Тіньовий стан PID */
    float pid_integrator;
    float last_error;
    
    /* Стан згладжування актуатора */
    float last_actuator_output;
    float transition_alpha;
} safe_supervisor_t;

/* Обчислення ентропії Шеннона для оцінки розмитості розподілу */
static float calculate_entropy(const float *probs, uint8_t count) {
    if (count <= 1) return 0.0f;
    float h = 0.0f;
    for (uint8_t i = 0; i < count; ++i) {
        if (probs[i] > 1e-6f) {
            h -= probs[i] * log2f(probs[i]);
        }
    }
    return h;
}

/* Оновлення ковзного вікна N з M */
static bool is_fault_persistent(safe_supervisor_t *sup, bool current_fault) {
    sup->fault_history[sup->fault_history_idx] = current_fault ? 1 : 0;
    sup->fault_history_idx = (sup->fault_history_idx + 1) % WINDOW_SIZE;
    
    uint8_t fault_count = 0;
    for (uint8_t i = 0; i < WINDOW_SIZE; ++i) {
        fault_count += sup->fault_history[i];
    }
    return fault_count >= sup->cfg.fault_threshold_n;
}

/* Ініціалізація супервізора */
void safe_supervisor_init(safe_supervisor_t *sup, const supervisor_config_t *cfg) {
    sup->cfg = *cfg;
    sup->state = SUPERVISOR_STATE_NOMINAL_ML;
    sup->last_valid_frame_ms = 0;
    sup->fault_history_idx = 0;
    sup->recovery_counter = 0;
    sup->pid_integrator = 0.0f;
    sup->last_error = 0.0f;
    sup->last_actuator_output = 0.0f;
    sup->transition_alpha = 1.0f;

    for (uint8_t i = 0; i < WINDOW_SIZE; ++i) {
        sup->fault_history[i] = 0;
    }
}

/* Виконання одного кроку наглядача */
float safe_supervisor_step(safe_supervisor_t *sup,
                           const ml_inference_frame_t *ml_frame,
                           const plant_feedback_t *fb,
                           uint32_t current_time_ms) {
    /* 1. Моніторинг здоров'я інференсу */
    bool timing_fault = (current_time_ms - ml_frame->timestamp_ms) > sup->cfg.deadline_timeout_ms;
    bool freshness_fault = !ml_frame->is_fresh;
    float entropy = calculate_entropy(ml_frame->class_probs, ml_frame->num_classes);
    bool entropy_fault = (entropy > sup->cfg.max_allowed_entropy);
    bool conf_fault = (ml_frame->confidence < sup->cfg.min_confidence_threshold);

    bool frame_fault = timing_fault || freshness_fault || entropy_fault || conf_fault;
    bool persistent_fault = is_fault_persistent(sup, frame_fault);

    if (!frame_fault) {
        sup->last_valid_frame_ms = current_time_ms;
    }

    /* 2. Розрахунок виходу детермінованого резервного правила (PID за IMU/сенсорами) */
    float error = fb->target_state - fb->current_state;
    float p_term = sup->cfg.kp * error;
    float d_term = -sup->cfg.kd * fb->current_rate;
    float u_rule = p_term + sup->pid_integrator + d_term;

    /* 3. Автомат станів Safe Supervisor */
    switch (sup->state) {
    case SUPERVISOR_STATE_NOMINAL_ML:
        if (persistent_fault) {
            sup->state = SUPERVISOR_STATE_RULE_FALLBACK;
            sup->recovery_counter = 0;
            sup->transition_alpha = 0.0f; /* Початок плавного переходу */
        } else if (frame_fault) {
            sup->state = SUPERVISOR_STATE_DEGRADED_HOLD;
        } else {
            /* Тіньове стеження: підтягуємо інтегратор під вихід нейромережі */
            if (sup->cfg.ki > 1e-5f) {
                sup->pid_integrator = ml_frame->u_cmd - p_term - d_term;
            }
        }
        break;

    case SUPERVISOR_STATE_DEGRADED_HOLD:
        if (persistent_fault) {
            sup->state = SUPERVISOR_STATE_RULE_FALLBACK;
            sup->recovery_counter = 0;
            sup->transition_alpha = 0.0f;
        } else if (!frame_fault) {
            sup->state = SUPERVISOR_STATE_NOMINAL_ML;
        }
        break;

    case SUPERVISOR_STATE_RULE_FALLBACK:
        /* Інтегрування для детермінованого контуру */
        sup->pid_integrator += sup->cfg.ki * error * sup->cfg.loop_dt_s;

        /* Гістерезис повернення */
        if (!frame_fault) {
            sup->recovery_counter++;
            if (sup->recovery_counter >= RECOVERY_TICKS) {
                sup->state = SUPERVISOR_STATE_NOMINAL_ML;
                sup->recovery_counter = 0;
            }
        } else {
            sup->recovery_counter = 0;
        }

        /* Критичний таймаут: якщо навіть правило не може втримати об'єкт */
        if (current_time_ms - sup->last_valid_frame_ms > 10000 && fabsf(error) > 45.0f) {
            sup->state = SUPERVISOR_STATE_EMERGENCY_SAFE;
        }
        break;

    case SUPERVISOR_STATE_EMERGENCY_SAFE:
        u_rule = 0.0f; /* Аварійний нуль або глушіння */
        break;
    }

    /* 4. Безударний перехід та генерація санкціонованого сигналу */
    float raw_target = 0.0f;
    if (sup->state == SUPERVISOR_STATE_NOMINAL_ML) {
        raw_target = ml_frame->u_cmd;
    } else if (sup->state == SUPERVISOR_STATE_DEGRADED_HOLD) {
        /* Екстраполяція останнього значення без ривків */
        raw_target = sup->last_actuator_output;
    } else if (sup->state == SUPERVISOR_STATE_RULE_FALLBACK) {
        if (sup->transition_alpha < 1.0f) {
            sup->transition_alpha += sup->cfg.loop_dt_s / 0.25f; /* 250 мс злиття */
            if (sup->transition_alpha > 1.0f) sup->transition_alpha = 1.0f;
        }
        raw_target = (1.0f - sup->transition_alpha) * sup->last_actuator_output +
                     sup->transition_alpha * u_rule;
    } else {
        raw_target = 0.0f;
    }

    /* 5. Обмеження швидкості наростання сигналу (Slew-Rate Limiter) */
    float max_delta = sup->cfg.max_slew_rate_deg_per_s * sup->cfg.loop_dt_s;
    float delta = raw_target - sup->last_actuator_output;
    if (delta > max_delta) delta = max_delta;
    if (delta < -max_delta) delta = -max_delta;

    float final_output = sup->last_actuator_output + delta;
    sup->last_actuator_output = final_output;
    sup->last_error = error;

    return final_output;
}
