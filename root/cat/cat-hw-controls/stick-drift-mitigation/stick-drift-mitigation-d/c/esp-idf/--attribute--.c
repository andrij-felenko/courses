#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define PROFILE_MAGIC 0x43414C49 // "CALI"

typedef struct __attribute__((packed)) {
    uint32_t magic;
    uint8_t version;
    uint16_t x_zero;
    uint16_t y_zero;
    float x_scale_neg;
    float x_scale_pos;
    float y_scale_neg;
    float y_scale_pos;
    uint16_t crc16;
} stick_profile_t;

uint16_t calculate_crc16(const uint8_t *data, size_t len) {
    uint16_t crc = 0xFFFF;
    for (size_t i = 0; i < len; i++) {
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

bool load_and_verify_profile(const uint8_t *nvram_buf, stick_profile_t *out_profile) {
    memcpy(out_profile, nvram_buf, sizeof(stick_profile_t));
    
    if (out_profile->magic != PROFILE_MAGIC) {
        return false; // Недійсний заголовок
    }

    // Обчислення CRC16 по всьому тілу структури крім останнього поля crc16
    size_t payload_len = sizeof(stick_profile_t) - sizeof(uint16_t);
    uint16_t expected_crc = calculate_crc16((const uint8_t*)out_profile, payload_len);

    if (out_profile->crc16 != expected_crc) {
        // Помилка STICK_ERR_INVALID_CALIB: завантажуємо дефолтні безпечні значення
        out_profile->x_zero = 2048;
        out_profile->y_zero = 2048;
        out_profile->x_scale_neg = 1.0f / 2048.0f;
        out_profile->x_scale_pos = 1.0f / 2047.0f;
        out_profile->y_scale_neg = 1.0f / 2048.0f;
        out_profile->y_scale_pos = 1.0f / 2047.0f;
        return false;
    }

    return true;
}
