#ifndef STICK_CALIBRATION_H
#define STICK_CALIBRATION_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define ADC_MAX_RESOLUTION    4095
#define ADC_MIN_SAFE_LIMIT    50
#define ADC_MAX_SAFE_LIMIT    4045
#define DEFAULT_DEADZONE      0.08f

// Прапорці статусу драйвера калібрування
typedef enum {
    STICK_STATUS_OK               = 0x00,
    STICK_STATUS_ERR_CRC          = 0x01,
    STICK_STATUS_ERR_SENSOR_FAULT = 0x02,
    STICK_STATUS_ERR_INVALID_PARAM= 0x04
} stick_status_flags_t;

// Профіль калібрування стіка (зберігається в EEPROM/Flash)
typedef struct {
    uint16_t adc_center_x;
    uint16_t adc_center_y;
    uint16_t adc_min_x;
    uint16_t adc_max_x;
    uint16_t adc_min_y;
    uint16_t adc_max_y;
    float    radial_deadzone;
    uint16_t crc16;
} stick_calibration_profile_t;

// Нормований вихідний вектор
typedef struct {
    float x;
    float y;
    float magnitude;
    bool  is_in_deadzone;
    uint8_t status_flags;
} stick_vector_t;

// Прототипи функцій
uint16_t calculate_crc16(const uint8_t *data, size_t length);

bool stick_calibrate_neutral(uint16_t (*read_adc_fn)(uint8_t channel),
                             stick_calibration_profile_t *profile,
                             size_t sample_count);

void stick_apply_calibration(const stick_calibration_profile_t *profile,
                             uint16_t raw_x,
                             uint16_t raw_y,
                             stick_vector_t *out_vec);

bool stick_save_profile(const stick_calibration_profile_t *profile, uint32_t eeprom_address);
bool stick_load_profile(stick_calibration_profile_t *profile, uint32_t eeprom_address);

#endif // STICK_CALIBRATION_H
