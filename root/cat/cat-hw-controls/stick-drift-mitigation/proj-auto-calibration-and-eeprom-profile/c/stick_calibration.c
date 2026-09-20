#include "stick_calibration.h"
#include "eeprom_driver.h"
#include <math.h>
#include <string.h>

// Обчислення CRC-16 (CCITT-FALSE, поліном 0x1021, початкове 0xFFFF)
uint16_t calculate_crc16(const uint8_t *data, size_t length) {
    uint16_t crc = 0xFFFF;
    for (size_t i = 0; i < length; i++) {
        crc ^= (uint16_t)data[i] << 8;
        for (uint8_t bit = 0; bit < 8; bit++) {
            if (crc & 0x8000) {
                crc = (crc << 1) ^ 0x1021;
            } else {
                crc <<= 1;
            }
        }
    }
    return crc;
}

// Автовизначення центру за вибіркою статичних даних в стані спокою
bool stick_calibrate_neutral(uint16_t (*read_adc_fn)(uint8_t channel),
                             stick_calibration_profile_t *profile,
                             size_t sample_count) {
    if (!read_adc_fn || !profile || sample_count == 0) {
        return false;
    }

    uint32_t sum_x = 0;
    uint32_t sum_y = 0;

    for (size_t i = 0; i < sample_count; i++) {
        uint16_t val_x = read_adc_fn(0);
        uint16_t val_y = read_adc_fn(1);

        // Перевірка апаратного збою сенсора (обрив або коротке замикання)
        if (val_x < ADC_MIN_SAFE_LIMIT || val_x > ADC_MAX_SAFE_LIMIT ||
            val_y < ADC_MIN_SAFE_LIMIT || val_y > ADC_MAX_SAFE_LIMIT) {
            return false;
        }

        sum_x += val_x;
        sum_y += val_y;
    }

    profile->adc_center_x = (uint16_t)(sum_x / sample_count);
    profile->adc_center_y = (uint16_t)(sum_y / sample_count);

    // За замовчуванням встановлюємо повні діапазони АЦП 12-біт
    profile->adc_min_x = 0;
    profile->adc_max_x = ADC_MAX_RESOLUTION;
    profile->adc_min_y = 0;
    profile->adc_max_y = ADC_MAX_RESOLUTION;

    profile->radial_deadzone = DEFAULT_DEADZONE;

    // Обчислення CRC16 для блоку даних структури без поля crc16
    size_t data_len = offsetof(stick_calibration_profile_t, crc16);
    profile->crc16 = calculate_crc16((const uint8_t *)profile, data_len);

    return true;
}

// Перетворення сирих АЦП координат у нормований вектор із радіальною мертвою зоною
void stick_apply_calibration(const stick_calibration_profile_t *profile,
                             uint16_t raw_x,
                             uint16_t raw_y,
                             stick_vector_t *out_vec) {
    if (!profile || !out_vec) {
        return;
    }

    memset(out_vec, 0, sizeof(stick_vector_t));

    // Верифікація контрольної суми профілю
    size_t data_len = offsetof(stick_calibration_profile_t, crc16);
    uint16_t calc_crc = calculate_crc16((const uint8_t *)profile, data_len);

    if (calc_crc != profile->crc16) {
        out_vec->status_flags |= STICK_STATUS_ERR_CRC;
        return;
    }

    // Перевірка відмови сенсора
    if (raw_x < ADC_MIN_SAFE_LIMIT || raw_x > ADC_MAX_SAFE_LIMIT ||
        raw_y < ADC_MIN_SAFE_LIMIT || raw_y > ADC_MAX_SAFE_LIMIT) {
        out_vec->status_flags |= STICK_STATUS_ERR_SENSOR_FAULT;
        return;
    }

    // Центрування відносно встановленого нуля
    float norm_x = 0.0f;
    float norm_y = 0.0f;

    if (raw_x >= profile->adc_center_x) {
        float range = (float)(profile->adc_max_x - profile->adc_center_x);
        norm_x = (range > 0.0f) ? ((float)(raw_x - profile->adc_center_x) / range) : 0.0f;
    } else {
        float range = (float)(profile->adc_center_x - profile->adc_min_x);
        norm_x = (range > 0.0f) ? -((float)(profile->adc_center_x - raw_x) / range) : 0.0f;
    }

    if (raw_y >= profile->adc_center_y) {
        float range = (float)(profile->adc_max_y - profile->adc_center_y);
        norm_y = (range > 0.0f) ? ((float)(raw_y - profile->adc_center_y) / range) : 0.0f;
    } else {
        float range = (float)(profile->adc_center_y - profile->adc_min_y);
        norm_y = (range > 0.0f) ? -((float)(profile->adc_center_y - raw_y) / range) : 0.0f;
    }

    // Обмеження діапазону [-1.0, 1.0]
    if (norm_x > 1.0f) norm_x = 1.0f;
    if (norm_x < -1.0f) norm_x = -1.0f;
    if (norm_y > 1.0f) norm_y = 1.0f;
    if (norm_y < -1.0f) norm_y = -1.0f;

    // Обчислення радіуса відхилення
    float radius = sqrtf(norm_x * norm_x + norm_y * norm_y);
    float deadzone = profile->radial_deadzone;

    if (radius <= deadzone) {
        out_vec->x = 0.0f;
        out_vec->y = 0.0f;
        out_vec->magnitude = 0.0f;
        out_vec->is_in_deadzone = true;
    } else {
        // Scaled Radial Deadzone (плавний перехід без стрибка чутливості)
        float scaled_mag = (radius - deadzone) / (1.0f - deadzone);
        if (scaled_mag > 1.0f) scaled_mag = 1.0f;

        out_vec->x = (norm_x / radius) * scaled_mag;
        out_vec->y = (norm_y / radius) * scaled_mag;
        out_vec->magnitude = scaled_mag;
        out_vec->is_in_deadzone = false;
    }

    out_vec->status_flags = STICK_STATUS_OK;
}

// Збереження профілю у пам'ять EEPROM
bool stick_save_profile(const stick_calibration_profile_t *profile, uint32_t eeprom_address) {
    if (!profile) return false;
    return eeprom_write_block(eeprom_address, (const uint8_t *)profile, sizeof(stick_calibration_profile_t));
}

// Завантаження та перевірка профілю з EEPROM
bool stick_load_profile(stick_calibration_profile_t *profile, uint32_t eeprom_address) {
    if (!profile) return false;

    if (!eeprom_read_block(eeprom_address, (uint8_t *)profile, sizeof(stick_calibration_profile_t))) {
        return false;
    }

    size_t data_len = offsetof(stick_calibration_profile_t, crc16);
    uint16_t calc_crc = calculate_crc16((const uint8_t *)profile, data_len);

    return (calc_crc == profile->crc16);
}
