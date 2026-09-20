#include "../include/pendant_driver.h"
#include <stdlib.h>
#include <string.h>

void pendant_init(pendant_safety_state_t *safety, pendant_joystick_t *joy) {
    if (safety) {
        safety->estop_ch1 = 0;
        safety->estop_ch2 = 0;
        safety->enabling_ch1 = 0;
        safety->enabling_ch2 = 0;
        safety->estop_status = ESTOP_TRIGGERED;
        safety->enabling_status = ENABLING_OFF_RELEASED;
        safety->discrepancy_start_ms = 0;
        safety->discrepancy_active = false;
        safety->safety_ok = false;
    }

    if (joy) {
        joy->raw_x = PENDANT_ADC_CENTER;
        joy->raw_y = PENDANT_ADC_CENTER;
        joy->raw_z = PENDANT_ADC_CENTER;
        joy->norm_x = 0;
        joy->norm_y = 0;
        joy->norm_z = 0;
        joy->deadband = 120U; // Нечутлива зона навколо 2048
    }
}

void pendant_update_safety(pendant_safety_state_t *safety,
                          uint8_t estop_1, uint8_t estop_2,
                          uint8_t enable_1, uint8_t enable_2,
                          uint32_t current_time_ms) {
    if (!safety) return;

    safety->estop_ch1 = estop_1;
    safety->estop_ch2 = estop_2;
    safety->enabling_ch1 = enable_1;
    safety->enabling_ch2 = enable_2;

    bool has_discrepancy = false;

    // 1. Крос-моніторинг каналів кнопки E-Stop
    if (estop_1 == 1 && estop_2 == 1) {
        safety->estop_status = ESTOP_OK;
    } else if (estop_1 == 0 && estop_2 == 0) {
        safety->estop_status = ESTOP_TRIGGERED;
    } else {
        has_discrepancy = true;
    }

    // 2. Крос-моніторинг каналів клавіша дозволу (Enabling Switch)
    if (enable_1 == enable_2) {
        switch (enable_1) {
            case 0:
                safety->enabling_status = ENABLING_OFF_RELEASED;
                break;
            case 1:
                safety->enabling_status = ENABLING_CENTER_ENABLED;
                break;
            case 2:
                safety->enabling_status = ENABLING_PANIC_COMPRESSED;
                break;
            default:
                has_discrepancy = true;
                break;
        }
    } else {
        has_discrepancy = true;
    }

    // 3. Обробка таймера неузгодженості (Discrepancy Timer)
    if (has_discrepancy) {
        if (!safety->discrepancy_active) {
            safety->discrepancy_active = true;
            safety->discrepancy_start_ms = current_time_ms;
        } else if ((current_time_ms - safety->discrepancy_start_ms) >= PENDANT_DISCREPANCY_TIMEOUT_MS) {
            if (estop_1 != estop_2) {
                safety->estop_status = ESTOP_FAULT_DISCREPANCY;
            }
            if (enable_1 != enable_2) {
                safety->enabling_status = ENABLING_FAULT_DISCREPANCY;
            }
        }
    } else {
        safety->discrepancy_active = false;
    }

    // 4. Формування підсумкового дозволу руху
    safety->safety_ok = (safety->estop_status == ESTOP_OK) &&
                        (safety->enabling_status == ENABLING_CENTER_ENABLED) &&
                        (!safety->discrepancy_active);
}

static int16_t process_axis(uint16_t raw_adc, uint16_t deadband) {
    int32_t diff = (int32_t)raw_adc - (int32_t)PENDANT_ADC_CENTER;

    if (abs((int)diff) <= (int)deadband) {
        return 0;
    }

    if (diff > 0) {
        diff -= deadband;
    } else {
        diff += deadband;
    }

    int32_t max_range = (int32_t)PENDANT_ADC_CENTER - (int32_t)deadband;
    if (max_range <= 0) return 0;

    int32_t scaled = (diff * 1000) / max_range;
    if (scaled > 1000) scaled = 1000;
    if (scaled < -1000) scaled = -1000;

    return (int16_t)scaled;
}

void pendant_update_joystick(pendant_joystick_t *joy,
                            uint16_t adc_x, uint16_t adc_y, uint16_t adc_z) {
    if (!joy) return;

    joy->raw_x = adc_x;
    joy->raw_y = adc_y;
    joy->raw_z = adc_z;

    joy->norm_x = process_axis(adc_x, joy->deadband);
    joy->norm_y = process_axis(adc_y, joy->deadband);
    joy->norm_z = process_axis(adc_z, joy->deadband);
}

uint16_t pendant_calculate_crc16(const uint8_t *data, size_t length) {
    uint16_t crc = 0xFFFFU;

    for (size_t i = 0; i < length; i++) {
        crc ^= (uint16_t)data[i];
        for (uint8_t j = 0; j < 8; j++) {
            if (crc & 0x0001U) {
                crc = (crc >> 1) ^ 0xA001U;
            } else {
                crc >>= 1;
            }
        }
    }
    return crc;
}

size_t pendant_serialize_frame(const pendant_safety_state_t *safety,
                               const pendant_joystick_t *joy,
                               uint8_t *buffer, size_t max_len) {
    if (!safety || !joy || !buffer || max_len < sizeof(pendant_frame_t)) {
        return 0;
    }

    pendant_frame_t frame;
    frame.header[0] = 0xAA;
    frame.header[1] = 0x55;

    uint8_t flags = 0;
    if (safety->estop_status == ESTOP_OK) flags |= (1U << 0);
    if (safety->enabling_status == ENABLING_CENTER_ENABLED) flags |= (1U << 1);
    if (safety->safety_ok) flags |= (1U << 2);
    if (safety->discrepancy_active) flags |= (1U << 3);

    frame.safety_flags = flags;
    frame.jog_x = safety->safety_ok ? joy->norm_x : 0;
    frame.jog_y = safety->safety_ok ? joy->norm_y : 0;
    frame.jog_z = safety->safety_ok ? joy->norm_z : 0;

    // Обчислення CRC по тілу кадру (без поля crc16)
    size_t payload_len = offsetof(pendant_frame_t, crc16);
    frame.crc16 = pendant_calculate_crc16((const uint8_t *)&frame, payload_len);

    memcpy(buffer, &frame, sizeof(pendant_frame_t));
    return sizeof(pendant_frame_t);
}
