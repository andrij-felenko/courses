#include <stdio.h>
#include <stdint.h>
#include <stddef.h>
#include <string.h>

#define PUF_BLOCK_SIZE 64 /* Розмір блоку SRAM PUF у байтах */

/* Обчислення кількості встановлених бітів (Вага Геммінга) для 8-бітного числа */
static uint8_t popcount8(uint8_t val) {
    uint8_t count = 0;
    while (val) {
        count += (val & 1);
        val >>= 1;
    }
    return count;
}

/* Обчислення відстані Геммінга (Intra-distance) між двома бітовими масивами */
uint32_t calculate_hamming_distance(const uint8_t *buf1, const uint8_t *buf2, size_t len) {
    uint32_t distance = 0;
    for (size_t i = 0; i < len; i++) {
        distance += popcount8(buf1[i] ^ buf2[i]);
    }
    return distance;
}

/* Зчитування первинного стану SRAM PUF одразу після скидання (симуляція фізичного регістру) */
void sram_puf_read_raw(uint8_t *buffer, size_t len, uint32_t power_cycle_seed) {
    /* Симуляція стабільного апаратного відбитка з невеликим шумом (Intra-noise) */
    static const uint8_t base_puf_fingerprint[PUF_BLOCK_SIZE] = {
        0xA5, 0x5A, 0x3C, 0xC3, 0xF0, 0x0F, 0xAA, 0x55,
        0x12, 0x34, 0x56, 0x78, 0x9A, 0xBC, 0xDE, 0xF0,
        0x4B, 0x68, 0x2D, 0xE9, 0x71, 0x3A, 0x8F, 0xC5,
        0x93, 0x52, 0xB1, 0xE4, 0x07, 0x6E, 0xD8, 0x2A,
        0xFE, 0xDC, 0xBA, 0x98, 0x76, 0x54, 0x32, 0x10,
        0x55, 0xAA, 0x0F, 0xF0, 0xC3, 0x3C, 0x5A, 0xA5,
        0x1E, 0x2D, 0x3C, 0x4B, 0x5A, 0x69, 0x78, 0x87,
        0x96, 0xA5, 0xB4, 0xC3, 0xD2, 0xE1, 0xF0, 0x0F
    };

    for (size_t i = 0; i < len && i < PUF_BLOCK_SIZE; i++) {
        /* Додавання температурного та напругового шуму (близько 3-5% бітових помилок) */
        uint8_t noise = (uint8_t)((power_cycle_seed * 1103515245 + 12345 + i) >> 16) & 0x07;
        buffer[i] = base_puf_fingerprint[i] ^ (1 << (noise % 8));
    }
}

/* Мажоритарне голосування для очищення шуму з N вибірок */
void sram_puf_majority_vote(const uint8_t samples[][PUF_BLOCK_SIZE], size_t num_samples, uint8_t *out_stable, size_t len) {
    for (size_t byte_idx = 0; byte_idx < len; byte_idx++) {
        uint8_t voted_byte = 0;
        for (int bit_idx = 0; bit_idx < 8; bit_idx++) {
            size_t ones_count = 0;
            for (size_t sample_idx = 0; sample_idx < num_samples; sample_idx++) {
                if ((samples[sample_idx][byte_idx] >> bit_idx) & 1) {
                    ones_count++;
                }
            }
            if (ones_count > num_samples / 2) {
                voted_byte |= (1 << bit_idx);
            }
        }
        out_stable[byte_idx] = voted_byte;
    }
}
