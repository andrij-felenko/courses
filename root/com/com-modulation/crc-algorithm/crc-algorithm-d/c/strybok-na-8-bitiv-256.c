#include <stdint.h>
#include <stddef.h>

#define CRC32_POLYNOMIAL 0x04C11DB7U

static uint32_t s_crc32_table[256];
static int s_is_table_ready = 0;

// Генерація таблиці залишків 256x32 біти
void crc32_table_init(void) {
    for (uint32_t i = 0; i < 256; i++) {
        uint32_t remainder = i << 24;
        for (int bit = 0; bit < 8; bit++) {
            if (remainder & 0x80000000U) {
                remainder = (remainder << 1) ^ CRC32_POLYNOMIAL;
            } else {
                remainder = (remainder << 1);
            }
        }
        s_crc32_table[i] = remainder;
    }
    s_is_table_ready = 1;
}

uint32_t crc32_table_lookup(const uint8_t *data, size_t length) {
    if (!s_is_table_ready) {
        crc32_table_init();
    }

    uint32_t crc = 0xFFFFFFFFU;
    for (size_t i = 0; i < length; i++) {
        uint8_t table_index = (uint8_t)((crc >> 24) ^ data[i]);
        crc = (crc << 8) ^ s_crc32_table[table_index];
    }

    return crc ^ 0xFFFFFFFFU;
}
