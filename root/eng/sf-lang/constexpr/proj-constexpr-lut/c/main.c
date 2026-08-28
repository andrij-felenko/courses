/* Традиційна реалізація на C: динамічна побудова таблиці в RAM */
#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#define CRC32_POLYNOMIAL 0xEDB88320u

static uint32_t crc32_table[256];
static bool is_table_initialized = false;

void crc32_init_table(void) {
    if (is_table_initialized) return;
    for (uint32_t i = 0; i < 256; ++i) {
        uint32_t crc = i;
        for (int bit = 0; bit < 8; ++bit) {
            if (crc & 1u) {
                crc = (crc >> 1) ^ CRC32_POLYNOMIAL;
            } else {
                crc >>= 1;
            }
        }
        crc32_table[i] = crc;
    }
    is_table_initialized = true;
}

uint32_t crc32_calculate(const uint8_t *data, size_t length) {
    if (!is_table_initialized) {
        crc32_init_table();
    }
    uint32_t crc = 0xFFFFFFFFu;
    for (size_t i = 0; i < length; ++i) {
        uint8_t index = (uint8_t)(crc ^ data[i]);
        crc = (crc >> 8) ^ crc32_table[index];
    }
    return crc ^ 0xFFFFFFFFu;
}
