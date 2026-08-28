#include <stdint.h>
#include <stddef.h>

#define CRC32_POLY_REV 0xEDB88320U

static uint32_t s_crc_table[8][256];
static int s_tables_initialized = 0;

void crc32_slice8_init(void) {
    if (s_tables_initialized) return;

    /* Базова таблиця T0 (зворотний поліном IEEE 802.3) */
    for (uint32_t i = 0; i < 256; i++) {
        uint32_t c = i;
        for (int b = 0; b < 8; b++) {
            c = (c & 1U) ? (c >> 1) ^ CRC32_POLY_REV : (c >> 1);
        }
        s_crc_table[0][i] = c;
    }

    /* Генерація таблиць T1..T7 для паралельних зсувів на 1..7 байтів */
    for (int k = 1; k < 8; k++) {
        for (uint32_t i = 0; i < 256; i++) {
            uint32_t prev = s_crc_table[k - 1][i];
            s_crc_table[k][i] = (prev >> 8) ^ s_crc_table[0][prev & 0xFFU];
        }
    }
    s_tables_initialized = 1;
}

uint32_t crc32_slice8_compute(const uint8_t *data, size_t length) {
    if (!s_tables_initialized) {
        crc32_slice8_init();
    }

    uint32_t crc = 0xFFFFFFFFU;
    const uint8_t *ptr = data;

    /* 1. Пролог: вирівнювання вказівника до 8-байтної межі в пам'яті */
    while (length > 0 && ((uintptr_t)ptr & 7U) != 0) {
        crc = (crc >> 8) ^ s_crc_table[0][(crc ^ *ptr) & 0xFFU];
        ptr++;
        length--;
    }

    /* 2. Основне тіло Slice-by-8: обробка по 64 біти (8 байтів) за ітерацію */
    while (length >= 8) {
        uint32_t low = *(const uint32_t *)ptr;
        uint32_t high = *(const uint32_t *)(ptr + 4);

        uint32_t term1 = low ^ crc;
        uint32_t term2 = high;

        crc = s_crc_table[7][term1 & 0xFFU]
            ^ s_crc_table[6][(term1 >> 8) & 0xFFU]
            ^ s_crc_table[5][(term1 >> 16) & 0xFFU]
            ^ s_crc_table[4][term1 >> 24]
            ^ s_crc_table[3][term2 & 0xFFU]
            ^ s_crc_table[2][(term2 >> 8) & 0xFFU]
            ^ s_crc_table[1][(term2 >> 16) & 0xFFU]
            ^ s_crc_table[0][term2 >> 24];

        ptr += 8;
        length -= 8;
    }

    /* 3. Епілог: обробка залишку буфера (1..7 байтів) */
    while (length > 0) {
        crc = (crc >> 8) ^ s_crc_table[0][(crc ^ *ptr) & 0xFFU];
        ptr++;
        length--;
    }

    return crc ^ 0xFFFFFFFFU;
}
