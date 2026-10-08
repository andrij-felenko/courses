/**
 * @file tcrt5000.c
 * @brief Реалізація драйвера масиву оптичних давачів TCRT5000.
 */

#include "../include/tcrt5000.h"
#include <stddef.h>

tcrt5000_status_t tcrt5000_init(const tcrt5000_config_t *config) {
    if (config == NULL) {
        return TCRT5000_ERROR_NULL_POINTER;
    }
    if (config->sensor_count == 0 || config->sensor_count > TCRT5000_MAX_SENSORS) {
        return TCRT5000_ERROR_INVALID_PARAM;
    }

    for (uint8_t i = 0; i < config->sensor_count; i++) {
        if (config->use_analog) {
            mcu_status_t st = mcu_adc_init_channel(config->adc_channels[i]);
            if (st != MCU_OK) {
                return TCRT5000_ERROR_HAL;
            }
        } else {
            mcu_status_t st = mcu_gpio_init_input(config->gpio_pins[i]);
            if (st != MCU_OK) {
                return TCRT5000_ERROR_HAL;
            }
        }
    }

    return TCRT5000_OK;
}

tcrt5000_status_t tcrt5000_calibration_reset(tcrt5000_calibration_t *calib, uint8_t sensor_count) {
    if (calib == NULL) {
        return TCRT5000_ERROR_NULL_POINTER;
    }
    if (sensor_count == 0 || sensor_count > TCRT5000_MAX_SENSORS) {
        return TCRT5000_ERROR_INVALID_PARAM;
    }

    for (uint8_t i = 0; i < sensor_count; i++) {
        calib->min_raw[i] = 0xFFFF;
        calib->max_raw[i] = 0;
    }
    calib->is_calibrated = false;

    return TCRT5000_OK;
}

tcrt5000_status_t tcrt5000_calibration_update(const tcrt5000_config_t *config,
                                               tcrt5000_calibration_t *calib) {
    if (config == NULL || calib == NULL) {
        return TCRT5000_ERROR_NULL_POINTER;
    }
    if (config->sensor_count == 0 || config->sensor_count > TCRT5000_MAX_SENSORS) {
        return TCRT5000_ERROR_INVALID_PARAM;
    }

    uint16_t current_raw[TCRT5000_MAX_SENSORS];
    uint8_t oversamples = (config->adc_oversample > 0) ? config->adc_oversample : 1;

    mcu_status_t st = mcu_adc_read_multi_oversampled(config->adc_channels,
                                                     config->sensor_count,
                                                     oversamples,
                                                     current_raw);
    if (st != MCU_OK) {
        return TCRT5000_ERROR_HAL;
    }

    for (uint8_t i = 0; i < config->sensor_count; i++) {
        if (current_raw[i] < calib->min_raw[i]) {
            calib->min_raw[i] = current_raw[i];
        }
        if (current_raw[i] > calib->max_raw[i]) {
            calib->max_raw[i] = current_raw[i];
        }
    }

    return TCRT5000_OK;
}

tcrt5000_status_t tcrt5000_calibration_finalize(tcrt5000_calibration_t *calib, uint8_t sensor_count) {
    if (calib == NULL) {
        return TCRT5000_ERROR_NULL_POINTER;
    }
    if (sensor_count == 0 || sensor_count > TCRT5000_MAX_SENSORS) {
        return TCRT5000_ERROR_INVALID_PARAM;
    }

    for (uint8_t i = 0; i < sensor_count; i++) {
        if (calib->max_raw[i] <= calib->min_raw[i] + 50) {
            calib->is_calibrated = false;
            return TCRT5000_ERROR_INVALID_PARAM;
        }
    }

    calib->is_calibrated = true;
    return TCRT5000_OK;
}

tcrt5000_status_t tcrt5000_read_digital(const tcrt5000_config_t *config,
                                        tcrt5000_reading_t *reading) {
    if (config == NULL || reading == NULL) {
        return TCRT5000_ERROR_NULL_POINTER;
    }

    for (uint8_t i = 0; i < config->sensor_count; i++) {
        bool bit = false;
        mcu_status_t st = mcu_gpio_read_pin(config->gpio_pins[i], &bit);
        if (st != MCU_OK) {
            return TCRT5000_ERROR_HAL;
        }
        reading->digital_bits[i] = bit;
    }

    return TCRT5000_OK;
}

int32_t tcrt5000_calculate_weighted_position(const uint16_t *normalized,
                                             uint8_t count,
                                             bool *out_line_detected) {
    if (normalized == NULL || count == 0) {
        if (out_line_detected) *out_line_detected = false;
        return 0;
    }

    uint64_t weighted_sum = 0;
    uint32_t total_sum = 0;

    for (uint8_t i = 0; i < count; i++) {
        uint32_t val = normalized[i];
        weighted_sum += (uint64_t)i * TCRT5000_WEIGHT_STEP * val;
        total_sum += val;
    }

    int32_t center = (int32_t)(((count - 1) * TCRT5000_WEIGHT_STEP) / 2);

    if (total_sum < TCRT5000_MIN_LINE_SUM) {
        if (out_line_detected) *out_line_detected = false;
        return center;
    }

    if (out_line_detected) *out_line_detected = true;

    return (int32_t)(weighted_sum / total_sum);
}

tcrt5000_status_t tcrt5000_read_analog(const tcrt5000_config_t *config,
                                       const tcrt5000_calibration_t *calib,
                                       tcrt5000_reading_t *reading) {
    if (config == NULL || calib == NULL || reading == NULL) {
        return TCRT5000_ERROR_NULL_POINTER;
    }
    if (!calib->is_calibrated) {
        return TCRT5000_ERROR_NOT_CALIBRATED;
    }

    uint8_t oversamples = (config->adc_oversample > 0) ? config->adc_oversample : 1;

    mcu_status_t st = mcu_adc_read_multi_oversampled(config->adc_channels,
                                                     config->sensor_count,
                                                     oversamples,
                                                     reading->raw_adc);
    if (st != MCU_OK) {
        return TCRT5000_ERROR_HAL;
    }

    for (uint8_t i = 0; i < config->sensor_count; i++) {
        uint16_t raw = reading->raw_adc[i];
        uint16_t min_v = calib->min_raw[i];
        uint16_t max_v = calib->max_raw[i];

        if (raw <= min_v) {
            reading->normalized[i] = 0;
        } else if (raw >= max_v) {
            reading->normalized[i] = TCRT5000_CALIB_SCALE;
        } else {
            uint32_t range = max_v - min_v;
            reading->normalized[i] = (uint16_t)(((uint32_t)(raw - min_v) * TCRT5000_CALIB_SCALE) / range);
        }
    }

    reading->line_position = tcrt5000_calculate_weighted_position(reading->normalized,
                                                                   config->sensor_count,
                                                                   &reading->line_detected);

    reading->center_position = (int32_t)(((config->sensor_count - 1) * TCRT5000_WEIGHT_STEP) / 2);
    reading->position_error = reading->line_position - reading->center_position;

    if (!reading->line_detected) {
        return TCRT5000_WARN_LINE_LOST;
    }

    return TCRT5000_OK;
}

tcrt5000_status_t tcrt5000_compute_motor_speeds(tcrt5000_pd_controller_t *pd,
                                                int32_t position_error,
                                                tcrt5000_motor_speed_t *speeds) {
    if (pd == NULL || speeds == NULL) {
        return TCRT5000_ERROR_NULL_POINTER;
    }

    int32_t derivative = position_error - pd->last_error;
    pd->last_error = position_error;

    float correction_f = (pd->kp * (float)position_error) + (pd->kd * (float)derivative);
    int32_t correction = (int32_t)correction_f;

    int32_t left = (int32_t)pd->base_speed + correction;
    int32_t right = (int32_t)pd->base_speed - correction;

    if (left > pd->max_speed) left = pd->max_speed;
    if (left < -pd->max_speed) left = -pd->max_speed;

    if (right > pd->max_speed) right = pd->max_speed;
    if (right < -pd->max_speed) right = -pd->max_speed;

    speeds->left_motor_speed = (int16_t)left;
    speeds->right_motor_speed = (int16_t)right;

    return TCRT5000_OK;
}
