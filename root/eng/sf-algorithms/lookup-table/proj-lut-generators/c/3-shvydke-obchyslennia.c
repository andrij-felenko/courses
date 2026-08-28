#include <stdint.h>
#include <stddef.h>

#define CRC32_POLYNOMIAL 0xEDB88320U

static uint32_t CRC32_TABLE[256];
static int CRC32_INITIALIZED = 0;

void crc32_init_table(void) {
    if (CRC32_INITIALIZED) return;
    for (uint32_t i = 0; i < 256; i++) {
        uint32_t crc = i;
        for (uint32_t j = 0; j < 8; j++) {
            crc = (crc & 1) ? ((crc >> 1) ^ CRC32_POLYNOMIAL) : (crc >> 1);
        }
        CRC32_TABLE[i] = crc;
    }
    CRC32_INITIALIZED = 1;
}

uint32_t crc32_calculate(const uint8_t *data, size_t length) {
    crc32_init_table();
    uint32_t crc = 0xFFFFFFFFU;
    for (size_t i = 0; i < length; i++) {
        /* Обчислюємо індекс у таблиці як XOR поточного байта з молодшим байтом CRC */
        uint8_t table_index = (uint8_t)((crc ^ data[i]) & 0xFF);
        /* Оновлюємо акумулятор за один такт зсуву та вибірки */
        crc = CRC32_TABLE[table_index] ^ (crc >> 8);
    }
    return crc ^ 0xFFFFFFFFU;
}
