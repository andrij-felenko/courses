#include "rvdt_driver.h"
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846f
#endif

void rvdt_init(rvdt_state_t *state, const rvdt_config_t *config) {
    if (!state) return;
    state->raw_angle_deg = 0.0f;
    state->filtered_angle_deg = 0.0f;
    state->v_s1 = 0.0f;
    state->v_s2 = 0.0f;
    state->sum_voltage = 0.0f;
    state->diff_voltage = 0.0f;
    state->error = RVDT_OK;
}

rvdt_error_t rvdt_process_sample(rvdt_state_t *state, const rvdt_config_t *config, float v_s1, float v_s2) {
    if (!state || !config) return RVDT_ERR_OPEN_CIRCUIT;

    state->v_s1 = v_s1;
    state->v_s2 = v_s2;
    state->sum_voltage = v_s1 + v_s2;
    state->diff_voltage = v_s1 - v_s2;
    state->error = RVDT_OK;

    // Самодіагностика обмоток за сумарною напругою
    if (state->sum_voltage < config->min_sum_voltage_v) {
        state->error |= RVDT_ERR_OPEN_CIRCUIT;
        return state->error;
    }
    if (state->sum_voltage > config->max_sum_voltage_v) {
        state->error |= RVDT_ERR_SHORT_CIRCUIT;
        return state->error;
    }

    // Обчислення кута через atan2 для інваріантності до амплітуди збудження
    float angle_rad = atan2f(state->diff_voltage, state->sum_voltage);
    float angle_deg = (angle_rad * 180.0f / (float)M_PI) - config->zero_offset_deg;

    state->raw_angle_deg = angle_deg;

    // Перевірка допустимого діапазону кута
    if (fabsf(angle_deg) > config->max_angle_deg) {
        state->error |= RVDT_ERR_OUT_OF_RANGE;
    }

    // Цифрова ФНЧ-фільтрація вибірок
    float a = config->alpha_filter;
    if (a < 0.01f) a = 0.01f;
    if (a > 1.0f) a = 1.0f;
    state->filtered_angle_deg = (a * angle_deg) + ((1.0f - a) * state->filtered_angle_deg);

    return state->error;
}

void rvdt_calibrate_zero(rvdt_state_t *state, rvdt_config_t *config) {
    if (!state || !config) return;
    config->zero_offset_deg += state->raw_angle_deg;
    state->raw_angle_deg = 0.0f;
    state->filtered_angle_deg = 0.0f;
}
