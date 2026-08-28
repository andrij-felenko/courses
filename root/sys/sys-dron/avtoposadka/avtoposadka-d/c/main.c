#include <stdint.h>
#include <stdbool.h>
#include <math.h>

typedef enum {
    GD_STATE_IN_AIR = 0,
    GD_STATE_GROUND_CONTACT,
    GD_STATE_MAYBE_LANDED,
    GD_STATE_LANDED,
    GD_STATE_DISARMED
} ground_detector_state_t;

typedef struct {
    float max_velocity_z;         // Поріг вертикальної швидкості (м/с, зазвичай 0.15)
    float max_angular_rate_rad;   // Поріг кутової швидкості (рад/с, ~0.25 рад/с ≈ 14 град/с)
    float throttle_hover_ratio;   // Частка газу від висіння для детекту (зазвичай 0.30)
    float ground_effect_alt_m;    // Зона екранного ефекту (м, зазвичай 1.5)
    uint32_t contact_time_ms;     // Час підтвердження первинного контакту (мс, 500)
    uint32_t landed_time_ms;      // Час фіксації повного приземлення (мс, 1000)
    uint32_t disarm_timeout_ms;   // Таймаут лінійного гасіння і розброєння (мс, 500)
} ground_detector_config_t;

typedef struct {
    ground_detector_state_t state;
    ground_detector_config_t cfg;
    uint32_t contact_start_ms;
    uint32_t maybe_landed_start_ms;
    uint32_t landed_start_ms;
    float    throttle_output;
    bool     i_terms_frozen;
    bool     disarm_commanded;
} ground_detector_t;

void ground_detector_init(ground_detector_t *gd, const ground_detector_config_t *cfg) {
    gd->state = GD_STATE_IN_AIR;
    gd->cfg = *cfg;
    gd->contact_start_ms = 0;
    gd->maybe_landed_start_ms = 0;
    gd->landed_start_ms = 0;
    gd->throttle_output = 1.0f;
    gd->i_terms_frozen = false;
    gd->disarm_commanded = false;
}

// Періодичний виклик у контурі навігації (50 Гц / кожні 20 мс)
void ground_detector_update(ground_detector_t *gd,
                            float vz_actual,
                            float gyro_norm_rad,
                            float current_throttle,
                            float hover_throttle,
                            float altitude_m,
                            uint32_t now_ms) {
    
    // Розрахунок порога тяги від поточного рівня зависання
    float throttle_threshold = hover_throttle * gd->cfg.throttle_hover_ratio;
    
    // Перевірка базових фізичних умов контакту
    bool low_thrust = (current_throttle <= throttle_threshold);
    bool near_zero_vz = (fabsf(vz_actual) <= gd->cfg.max_velocity_z);
    bool gyro_quiet = (gyro_norm_rad <= gd->cfg.max_angular_rate_rad);
    bool physical_contact = low_thrust && near_zero_vz && gyro_quiet;

    switch (gd->state) {
        case GD_STATE_IN_AIR: {
            gd->i_terms_frozen = false;
            gd->disarm_commanded = false;

            if (physical_contact) {
                gd->state = GD_STATE_GROUND_CONTACT;
                gd->contact_start_ms = now_ms;
            }
            break;
        }

        case GD_STATE_GROUND_CONTACT: {
            if (!physical_contact) {
                // Відрив або порив вітру — повернення в повітря
                gd->state = GD_STATE_IN_AIR;
                break;
            }

            if ((now_ms - gd->contact_start_ms) >= gd->cfg.contact_time_ms) {
                gd->state = GD_STATE_MAYBE_LANDED;
                gd->maybe_landed_start_ms = now_ms;
                gd->i_terms_frozen = true; // Блокування розгону I-термів
            }
            break;
        }

        case GD_STATE_MAYBE_LANDED: {
            if (!physical_contact) {
                // Дрон підстрибнув або перекинувся
                gd->state = GD_STATE_IN_AIR;
                gd->i_terms_frozen = false;
                break;
            }

            if ((now_ms - gd->maybe_landed_start_ms) >= gd->cfg.landed_time_ms) {
                gd->state = GD_STATE_LANDED;
                gd->landed_start_ms = now_ms;
            }
            break;
        }

        case GD_STATE_LANDED: {
            // Лінійне плавне зниження обертів (Ramp down)
            uint32_t elapsed = now_ms - gd->landed_start_ms;
            if (elapsed < gd->cfg.disarm_timeout_ms) {
                float ramp_factor = 1.0f - ((float)elapsed / (float)gd->cfg.disarm_timeout_ms);
                gd->throttle_output = current_throttle * ramp_factor;
            } else {
                gd->throttle_output = 0.0f;
                gd->disarm_commanded = true;
                gd->state = GD_STATE_DISARMED;
            }
            break;
        }

        case GD_STATE_DISARMED:
        default: {
            gd->throttle_output = 0.0f;
            gd->disarm_commanded = true;
            gd->i_terms_frozen = true;
            break;
        }
    }
}
