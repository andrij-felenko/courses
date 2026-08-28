#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define THERMAL_MAX_SENSORS        3
#define THERMAL_DWELL_TIME_MS      5000
#define THERMAL_DT_MAX_SLEW_RATE   5.0f   // °C/с

typedef enum {
    THERMAL_STATE_NORMAL = 0,
    THERMAL_STATE_WARMING,
    THERMAL_STATE_THROTTLED,
    THERMAL_STATE_CRITICAL,
    THERMAL_STATE_SHUTDOWN
} thermal_state_t;

typedef struct {
    float temp_celsius;
    float temp_limit_crit;
    float temp_limit_warn;
    float prev_temp;
    float slew_rate;
} thermal_sensor_t;

typedef struct {
    float kp;
    float ki;
    float target_temp;
    float i_term;
    float i_min;
    float i_max;
} thermal_pi_controller_t;

typedef struct {
    thermal_state_t state;
    thermal_sensor_t sensors[THERMAL_MAX_SENSORS];
    size_t sensor_count;
    thermal_pi_controller_t pi;
    float throttle_factor;       // 1.0 = 100% потужності, 0.2 = 20%
    uint32_t state_entry_time_ms;
    uint32_t last_update_time_ms;
} thermal_manager_t;

// Ініціалізація модуля термоконтролера
void thermal_manager_init(thermal_manager_t *mgr) {
    if (!mgr) return;

    mgr->state = THERMAL_STATE_NORMAL;
    mgr->sensor_count = 3;
    mgr->throttle_factor = 1.0f;
    mgr->state_entry_time_ms = 0;
    mgr->last_update_time_ms = 0;

    // Давач 0: MCU Junction
    mgr->sensors[0] = (thermal_sensor_t){
        .temp_celsius = 25.0f, .temp_limit_warn = 60.0f,
        .temp_limit_crit = 100.0f, .prev_temp = 25.0f, .slew_rate = 0.0f
    };
    // Давач 1: Power MOSFETs
    mgr->sensors[1] = (thermal_sensor_t){
        .temp_celsius = 25.0f, .temp_limit_warn = 65.0f,
        .temp_limit_crit = 90.0f, .prev_temp = 25.0f, .slew_rate = 0.0f
    };
    // Давач 2: Battery Pack
    mgr->sensors[2] = (thermal_sensor_t){
        .temp_celsius = 25.0f, .temp_limit_warn = 45.0f,
        .temp_limit_crit = 60.0f, .prev_temp = 25.0f, .slew_rate = 0.0f
    };

    // Налаштування ПІ-регулятора
    mgr->pi = (thermal_pi_controller_t){
        .kp = 0.04f,
        .ki = 0.01f,
        .target_temp = 72.0f,
        .i_term = 0.0f,
        .i_min = -0.80f,
        .i_max = 0.0f
    };
}

// Оновлення показників термодавача та розрахунок похідної dT/dt
static void update_sensor_telemetry(thermal_sensor_t *s, float new_val, float dt_sec) {
    if (dt_sec > 0.001f) {
        s->slew_rate = (new_val - s->prev_temp) / dt_sec;
    }
    s->prev_temp = s->temp_celsius;
    s->temp_celsius = new_val;
}

// Затискання числа в діапазон
static float clamp_f(float val, float min, float max) {
    if (val < min) return min;
    if (val > max) return max;
    return val;
}

// Головний крок автомата термозахисту (викликається періодично)
void thermal_manager_update(thermal_manager_t *mgr, const float raw_temps[], uint32_t current_time_ms) {
    if (!mgr || !raw_temps) return;

    float dt_sec = (current_time_ms - mgr->last_update_time_ms) / 1000.0f;
    if (dt_sec <= 0.0f) dt_sec = 0.05f;
    mgr->last_update_time_ms = current_time_ms;

    float max_normalized_stress = 0.0f;
    float max_absolute_temp = 0.0f;
    bool thermal_shock_detected = false;

    for (size_t i = 0; i < mgr->sensor_count; ++i) {
        update_sensor_telemetry(&mgr->sensors[i], raw_temps[i], dt_sec);

        if (mgr->sensors[i].temp_celsius > max_absolute_temp) {
            max_absolute_temp = mgr->sensors[i].temp_celsius;
        }

        float stress = mgr->sensors[i].temp_celsius / mgr->sensors[i].temp_limit_crit;
        if (stress > max_normalized_stress) {
            max_normalized_stress = stress;
        }

        // Перевірка теплового удару за похідною dT/dt
        if (mgr->sensors[i].slew_rate > THERMAL_DT_MAX_SLEW_RATE) {
            thermal_shock_detected = true;
        }
    }

    uint32_t time_in_state = current_time_ms - mgr->state_entry_time_ms;
    thermal_state_t next_state = mgr->state;

    // Прямий аварійний тригер від теплового удару
    if (thermal_shock_detected || max_normalized_stress >= 1.0f) {
        next_state = THERMAL_STATE_SHUTDOWN;
    } else {
        switch (mgr->state) {
            case THERMAL_STATE_NORMAL:
                if (max_normalized_stress >= 0.70f) {
                    next_state = THERMAL_STATE_WARMING;
                }
                mgr->throttle_factor = 1.0f;
                mgr->pi.i_term = 0.0f;
                break;

            case THERMAL_STATE_WARMING:
                if (max_normalized_stress >= 0.85f) {
                    next_state = THERMAL_STATE_THROTTLED;
                } else if (max_normalized_stress < 0.60f && time_in_state >= THERMAL_DWELL_TIME_MS) {
                    next_state = THERMAL_STATE_NORMAL;
                }
                mgr->throttle_factor = 1.0f;
                break;

            case THERMAL_STATE_THROTTLED:
                if (max_normalized_stress >= 0.95f) {
                    next_state = THERMAL_STATE_CRITICAL;
                } else if (max_normalized_stress < 0.75f && time_in_state >= THERMAL_DWELL_TIME_MS) {
                    next_state = THERMAL_STATE_WARMING;
                } else {
                    // Розрахунок ПІ-регулювання в активній зоні
                    float err = mgr->pi.target_temp - max_absolute_temp;
                    mgr->pi.i_term += mgr->pi.ki * err * dt_sec;
                    mgr->pi.i_term = clamp_f(mgr->pi.i_term, mgr->pi.i_min, mgr->pi.i_max);

                    float p_term = mgr->pi.kp * err;
                    float raw_k = 1.0f + (p_term + mgr->pi.i_term);
                    mgr->throttle_factor = clamp_f(raw_k, 0.20f, 1.00f);
                }
                break;

            case THERMAL_STATE_CRITICAL:
                if (max_normalized_stress < 0.85f && time_in_state >= THERMAL_DWELL_TIME_MS) {
                    next_state = THERMAL_STATE_THROTTLED;
                }
                mgr->throttle_factor = 0.20f;  // Режим аварійного доповзання (Limp mode)
                break;

            case THERMAL_STATE_SHUTDOWN:
                mgr->throttle_factor = 0.0f;
                break;
        }
    }

    if (next_state != mgr->state) {
        mgr->state = next_state;
        mgr->state_entry_time_ms = current_time_ms;
    }
}
