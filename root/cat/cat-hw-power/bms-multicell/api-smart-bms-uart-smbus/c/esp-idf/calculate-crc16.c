// Приклад обробки таймауту зчитування BMS для ESP-IDF / STM32 (C)
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

typedef enum {
    BMS_DRIVER_OK = 0,
    BMS_DRIVER_ERR_TIMEOUT,
    BMS_DRIVER_ERR_CRC
} bms_driver_status_t;

uint16_t calculate_crc16(const uint8_t *data, uint16_t len) {
    uint16_t crc = 0xFFFF;
    for (uint16_t i = 0; i < len; i++) {
        crc ^= data[i];
        for (uint8_t j = 0; j < 8; j++) {
            if (crc & 0x0001) {
                crc = (crc >> 1) ^ 0xA001;
            } else {
                crc >>= 1;
            }
        }
    }
    return crc;
}

bms_driver_status_t parse_bms_frame(const uint8_t *frame, uint16_t frame_len) {
    if (frame_len < 7) {
        return BMS_DRIVER_ERR_TIMEOUT;
    }
    uint16_t received_crc = (frame[frame_len - 2] << 8) | frame[frame_len - 1];
    uint16_t computed_crc = calculate_crc16(frame, frame_len - 2);

    if (received_crc != computed_crc) {
        return BMS_DRIVER_ERR_CRC;
    }
    return BMS_DRIVER_OK;
}
