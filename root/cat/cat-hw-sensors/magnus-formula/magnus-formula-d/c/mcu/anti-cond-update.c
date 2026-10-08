#include <stdbool.h>
#include <stdint.h>
#include <math.h>

typedef enum {
    ANTI_COND_OFF = 0,
    ANTI_COND_HEATING,
    ANTI_COND_FAULT
} anti_cond_state_t;

typedef struct {
    float margin_on_c;        // Поріг увімкнення (ΔT_ON, наприклад 1.5°C)
    float margin_off_c;       // Поріг вимкнення (ΔT_OFF, наприклад 3.5°C)
    uint32_t max_heat_time_s; // Максимальний час безперервного нагріву [с]
} anti_cond_config_t;

typedef struct {
    anti_cond_state_t state;  // Поточний стан регулятора
    uint32_t heat_start_time_s; // Час початку нагріву
    bool heater_output;       // Стан виходу нагрівача (true = увімкнено)
} anti_cond_controller_t;

// Оновлення стану алгоритму захисту від конденсату (C)
void anti_cond_update(anti_cond_controller_t *ctrl, const anti_cond_config_t *cfg,
                      float surface_temp_c, float dew_point_c,
                      bool sensors_ok, uint32_t current_time_s) {
    if (!sensors_ok || isnan(surface_temp_c) || isnan(dew_point_c)) {
        ctrl->state = ANTI_COND_FAULT;
        ctrl->heater_output = false; // Безпечний стан при збої давачів
        return;
    }

    float margin = surface_temp_c - dew_point_c;

    switch (ctrl->state) {
        case ANTI_COND_OFF:
        case ANTI_COND_FAULT:
            if (margin <= cfg->margin_on_c) {
                ctrl->state = ANTI_COND_HEATING;
                ctrl->heater_output = true;
                ctrl->heat_start_time_s = current_time_s;
            }
            break;

        case ANTI_COND_HEATING:
            // Перевірка перевищення максимального часу роботи нагрівача
            if ((current_time_s - ctrl->heat_start_time_s) >= cfg->max_heat_time_s) {
                ctrl->state = ANTI_COND_FAULT;
                ctrl->heater_output = false;
            } else if (margin >= cfg->margin_off_c) {
                ctrl->state = ANTI_COND_OFF;
                ctrl->heater_output = false;
            }
            break;
    }
}
