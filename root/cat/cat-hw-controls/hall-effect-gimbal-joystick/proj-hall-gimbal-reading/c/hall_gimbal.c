#include "hall_gimbal.h"
#include <math.h>

// Перевірка коректності калібрування осі
static bool validate_axis_calib(const axis_calib_t *calib) {
    return (calib->min_raw < calib->center_raw) && (calib->center_raw < calib->max_raw);
}

hall_gimbal_status_t hall_gimbal_init(hall_gimbal_t *gimbal, const hall_gimbal_config_t *config) {
    if (!gimbal || !config) {
        return HALL_GIMBAL_ERR_INVALID_CALIB;
    }

    if (!validate_axis_calib(&config->axis_x) || !validate_axis_calib(&config->axis_y)) {
        return HALL_GIMBAL_ERR_INVALID_CALIB;
    }

    gimbal->config = *config;
    gimbal->ema_x_raw = (float)config->axis_x.center_raw;
    gimbal->ema_y_raw = (float)config->axis_y.center_raw;
    gimbal->initialized = true;

    return HALL_GIMBAL_OK;
}

// Нормалізація сирого значення осі відносно центру в діапазон [-1.0, 1.0]
static float map_axis_value(float filtered_raw, const axis_calib_t *calib) {
    if (filtered_raw < (float)calib->center_raw) {
        float span = (float)(calib->center_raw - calib->min_raw);
        if (span <= 0.0f) return -1.0f;
        float val = (filtered_raw - (float)calib->center_raw) / span;
        return (val < -1.0f) ? -1.0f : val;
    } else {
        float span = (float)(calib->max_raw - calib->center_raw);
        if (span <= 0.0f) return 1.0f;
        float val = (filtered_raw - (float)calib->center_raw) / span;
        return (val > 1.0f) ? 1.0f : val;
    }
}

hall_gimbal_output_t hall_gimbal_process(hall_gimbal_t *gimbal, uint16_t raw_x, uint16_t raw_y) {
    hall_gimbal_output_t out = { .x = 0.0f, .y = 0.0f, .status = HALL_GIMBAL_OK };

    if (!gimbal || !gimbal->initialized) {
        out.status = HALL_GIMBAL_ERR_INVALID_CALIB;
        return out;
    }

    // 1. Перевірка на апаратний вихід за межі (обрив лінії Холла або відпадання магніту)
    const uint16_t margin = 50; // Допустимий зазор за межами мін/макс
    if (raw_x < (gimbal->config.axis_x.min_raw > margin ? gimbal->config.axis_x.min_raw - margin : 0) ||
        raw_x > gimbal->config.axis_x.max_raw + margin ||
        raw_y < (gimbal->config.axis_y.min_raw > margin ? gimbal->config.axis_y.min_raw - margin : 0) ||
        raw_y > gimbal->config.axis_y.max_raw + margin) {
        out.status = HALL_GIMBAL_ERR_OUT_OF_RANGE;
        return out;
    }

    // 2. Експоненційне згладжування фільтром EMA (Exponential Moving Average)
    float alpha = gimbal->config.alpha_ema;
    gimbal->ema_x_raw = alpha * (float)raw_x + (1.0f - alpha) * gimbal->ema_x_raw;
    gimbal->ema_y_raw = alpha * (float)raw_y + (1.0f - alpha) * gimbal->ema_y_raw;

    // 3. Нормалізація осей у діапазон [-1.0, +1.0]
    float norm_x = map_axis_value(gimbal->ema_x_raw, &gimbal->config.axis_x);
    float norm_y = map_axis_value(gimbal->ema_y_raw, &gimbal->config.axis_y);

    // 4. Застосування радіальної мертвої зони (Radial Deadzone)
    float magnitude = sqrtf(norm_x * norm_x + norm_y * norm_y);
    float dz = gimbal->config.deadzone_radial;

    if (magnitude <= dz) {
        out.x = 0.0f;
        out.y = 0.0f;
    } else {
        // Ресштабування вектора після мертвї зони для плавності від 0.0 до 1.0
        float scaled_mag = (magnitude - dz) / (1.0f - dz);
        if (scaled_mag > 1.0f) scaled_mag = 1.0f;

        out.x = (norm_x / magnitude) * scaled_mag;
        out.y = (norm_y / magnitude) * scaled_mag;
    }

    return out;
}
