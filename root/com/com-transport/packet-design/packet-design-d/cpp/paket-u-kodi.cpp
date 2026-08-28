#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#define SYNC 0xAA

// CRC-8, поліном 0x07 (x⁸+x²+x+1) — без таблиці, для наочності
uint8_t crc8(const uint8_t *p, size_t n) {
    uint8_t crc = 0x00;
    for (size_t i = 0; i < n; i++) {
        crc ^= p[i];
        for (int b = 0; b < 8; b++)
            crc = (crc & 0x80) ? (uint8_t)((crc << 1) ^ 0x07)
                               : (uint8_t)(crc << 1);
    }
    return crc;
}
