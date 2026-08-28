#ifndef SENSOR_STATE_RECOVERY_H
#define SENSOR_STATE_RECOVERY_H

#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define MAX_SHADOW_REGISTERS 16
#define MAX_CALIBRATION_BYTES 32

typedef struct {
    uint8_t reg_addr;
    uint8_t value;
} shadow_reg_entry_t;

typedef struct {
    shadow_reg_entry_t registers[MAX_SHADOW_REGISTERS];
    uint8_t reg_count;
    uint8_t calib_data[MAX_CALIBRATION_BYTES];
    uint8_t calib_length;
    uint16_t calib_crc16;
    bool calib_valid;
} sensor_shadow_cache_t;

static inline uint16_t calculate_crc16_ccitt(const uint8_t *data, size_t length) {
    uint16_t crc = 0xFFFF;
    for (size_t i = 0; i < length; i++) {
        crc ^= (uint16_t)data[i] << 8;
        for (uint8_t bit = 0; bit < 8; bit++) {
            if (crc & 0x8000) {
                crc = (crc << 1) ^ 0x1021;
            } else {
                crc = crc << 1;
            }
        }
    }
    return crc;
}

void shadow_cache_init(sensor_shadow_cache_t *cache) {
    memset(cache, 0, sizeof(sensor_shadow_cache_t));
}

void shadow_cache_set_reg(sensor_shadow_cache_t *cache, uint8_t reg_addr, uint8_t value) {
    for (uint8_t i = 0; i < cache->reg_count; i++) {
        if (cache->registers[i].reg_addr == reg_addr) {
            cache->registers[i].value = value;
            return;
        }
    }
    if (cache->reg_count < MAX_SHADOW_REGISTERS) {
        cache->registers[cache->reg_count].reg_addr = reg_addr;
        cache->registers[cache->reg_count].value = value;
        cache->reg_count++;
    }
}

void shadow_cache_store_calib(sensor_shadow_cache_t *cache, const uint8_t *calib, uint8_t length) {
    if (length > MAX_CALIBRATION_BYTES) length = MAX_CALIBRATION_BYTES;
    memcpy(cache->calib_data, calib, length);
    cache->calib_length = length;
    cache->calib_crc16 = calculate_crc16_ccitt(calib, length);
    cache->calib_valid = true;
}

bool shadow_cache_verify_calib(const sensor_shadow_cache_t *cache, const uint8_t *calib, uint8_t length) {
    if (!cache->calib_valid || length != cache->calib_length) return false;
    uint16_t crc = calculate_crc16_ccitt(calib, length);
    return crc == cache->calib_crc16;
}

#endif // SENSOR_STATE_RECOVERY_H
