#include "crc16.h"

uint16_t crc16_ccitt(const void *data, size_t len, uint16_t seed)
{
    const uint8_t *p = (const uint8_t *)data;
    uint16_t crc = seed;

    while (len-- != 0u) {
        crc ^= (uint16_t)((uint16_t)(*p++) << 8);
        for (unsigned bit = 0u; bit < 8u; ++bit) {
            if ((crc & 0x8000u) != 0u) {
                crc = (uint16_t)((uint16_t)(crc << 1) ^ 0x1021u);
            } else {
                crc = (uint16_t)(crc << 1);
            }
        }
    }
    return crc;
}
