#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

uint16_t telemetry_crc16_ccitt(const uint8_t *data, size_t length) {
    uint16_t crc = 0xFFFF;
    for (size_t i = 0; i < length; ++i) {
        crc ^= (uint16_t)data[i] << 8;
        for (int b = 0; b < 8; ++b) {
            if (crc & 0x8000) {
                crc = (crc << 1) ^ 0x1021;
            } else {
                crc = crc << 1;
            }
        }
    }
    return crc;
}

bool telemetry_verify_frame(const uint8_t *frame_24b) {
    uint16_t expected_crc = ((uint16_t)frame_24b[22] << 8) | frame_24b[23];
    uint16_t calc_crc = telemetry_crc16_ccitt(frame_24b, 22);
    return expected_crc == calc_crc;
}
