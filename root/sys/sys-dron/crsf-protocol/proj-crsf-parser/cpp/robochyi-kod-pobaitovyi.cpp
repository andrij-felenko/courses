#include <stdint.h>
#include <string.h>

// ── CRC8/DVB-S2, поліном 0xD5 ────────────────────────────────────────────────
// Таблиця на 256 входів; будуємо один раз, далі кожен байт — одна вибірка.
static uint8_t crc8_table[256];

void crsf_crc8_init(void) {
    for (int i = 0; i < 256; ++i) {
        uint8_t crc = (uint8_t)i;
        for (int b = 0; b < 8; ++b)
            crc = (crc & 0x80) ? (uint8_t)((crc << 1) ^ 0xD5)
                               : (uint8_t)(crc << 1);
        crc8_table[i] = crc;
    }
}

static inline uint8_t crsf_crc8(const uint8_t *ptr, uint8_t len) {
    uint8_t crc = 0;
    for (uint8_t i = 0; i < len; ++i)
        crc = crc8_table[crc ^ ptr[i]];
    return crc;
}
