#include <stdint.h>
#include <stdbool.h>

typedef enum {
    THERMAL_STATE_NORMAL = 0,
    THERMAL_STATE_THROTTLING,
    THERMAL_STATE_SHUTDOWN
} thermal_state_t;

typedef struct {
    float t_warn;       // Попереджувальна температура (°C)
    float t_crit;       // Критична температура (°C)
    float t_hyst;       // Гістерезис повернення (°C)
    float i_max;        // Максимальний струм (А)
    float i_min;        // Мінімальний струм у тротлінгу (А)
} thermal_config_t;

typedef struct {
    thermal_state_t state;
    float current_limit;
    bool bridge_enabled;
} thermal_protection_t;

void thermal_protection_update(thermal_protection_t *prot, const thermal_config_t *cfg, float t_winding) {
    switch (prot->state) {
        case THERMAL_STATE_NORMAL:
            if (t_winding >= cfg->t_crit) {
                prot->state = THERMAL_STATE_SHUTDOWN;
                prot->bridge_enabled = false;
                prot->current_limit = 0.0f;
            } else if (t_winding >= cfg->t_warn) {
                prot->state = THERMAL_STATE_THROTTLING;
                prot->bridge_enabled = true;
            } else {
                prot->bridge_enabled = true;
                prot->current_limit = cfg->i_max;
            }
            break;

        case THERMAL_STATE_THROTTLING:
            if (t_winding >= cfg->t_crit) {
                prot->state = THERMAL_STATE_SHUTDOWN;
                prot->bridge_enabled = false;
                prot->current_limit = 0.0f;
            } else if (t_winding < (cfg->t_warn - cfg->t_hyst)) {
                prot->state = THERMAL_STATE_NORMAL;
                prot->bridge_enabled = true;
                prot->current_limit = cfg->i_max;
            }
            break;

        case THERMAL_STATE_SHUTDOWN:
            if (t_winding < (cfg->t_crit - cfg->t_hyst)) {
                prot->state = THERMAL_STATE_THROTTLING;
                prot->bridge_enabled = true;
            }
            break;
    }

    // Обчислення плавної величини обмеження струму у режимі тротлінгу
    if (prot->state == THERMAL_STATE_THROTTLING) {
        float ratio = (t_winding - cfg->t_warn) / (cfg->t_crit - cfg->t_warn);
        if (ratio > 1.0f) ratio = 1.0f;
        if (ratio < 0.0f) ratio = 0.0f;
        prot->current_limit = cfg->i_max - ratio * (cfg->i_max - cfg->i_min);
    }
}
