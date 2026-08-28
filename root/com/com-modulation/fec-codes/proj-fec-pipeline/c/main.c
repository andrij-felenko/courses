#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define ROWS 4
#define COLS 7
#define DATA_BITS 4

/* Систематичний кодер Hamming(7, 4) */
uint8_t hamming_encode_nibble(uint8_t data) {
    uint8_t d0 = (data >> 0) & 1;
    uint8_t d1 = (data >> 1) & 1;
    uint8_t d2 = (data >> 2) & 1;
    uint8_t d3 = (data >> 3) & 1;

    uint8_t p0 = d0 ^ d1 ^ d2;
    uint8_t p1 = d1 ^ d2 ^ d3;
    uint8_t p2 = d0 ^ d1 ^ d3;

    return (uint8_t)(d0 | (d1 << 1) | (d2 << 2) | (d3 << 3) |
                    (p0 << 4) | (p1 << 5) | (p2 << 6));
}

/* Синдромний декодер Hamming(7, 4) з виправленням 1 помилки */
uint8_t hamming_decode_codeword(uint8_t code, bool *corrected, int *error_index) {
    uint8_t r[7];
    for (int i = 0; i < 7; ++i) {
        r[i] = (code >> i) & 1;
    }

    uint8_t s0 = r[4] ^ r[0] ^ r[1] ^ r[2];
    uint8_t s1 = r[5] ^ r[1] ^ r[2] ^ r[3];
    uint8_t s2 = r[6] ^ r[0] ^ r[1] ^ r[3];
    uint8_t syndrome = (uint8_t)(s0 | (s1 << 1) | (s2 << 2));

    *corrected = false;
    *error_index = -1;

    if (syndrome != 0) {
        *corrected = true;
        /* Таблиця відповідності синдрому позиції пошкодженого біта */
        int error_pos = -1;
        switch (syndrome) {
            case 0b101: error_pos = 0; break; /* d0 */
            case 0b111: error_pos = 1; break; /* d1 */
            case 0b011: error_pos = 2; break; /* d2 */
            case 0b110: error_pos = 3; break; /* d3 */
            case 0b001: error_pos = 4; break; /* p0 */
            case 0b010: error_pos = 5; break; /* p1 */
            case 0b100: error_pos = 6; break; /* p2 */
            default:    error_pos = -1; break;
        }
        *error_index = error_pos;
        if (error_pos >= 0 && error_pos < 7) {
            r[error_pos] ^= 1; /* Інверсія пошкодженого біта */
        }
    }

    return (uint8_t)(r[0] | (r[1] << 1) | (r[2] << 2) | (r[3] << 3));
}

/* Матричний блоковий переміжник */
void matrix_interleave(const uint8_t in_codewords[ROWS], uint8_t out_stream[ROWS * COLS]) {
    for (int col = 0; col < COLS; ++col) {
        for (int row = 0; row < ROWS; ++row) {
            uint8_t bit = (in_codewords[row] >> col) & 1;
            out_stream[col * ROWS + row] = bit;
        }
    }
}

/* Зворотний депереміжник */
void matrix_deinterleave(const uint8_t in_stream[ROWS * COLS], uint8_t out_codewords[ROWS]) {
    memset(out_codewords, 0, ROWS);
    for (int col = 0; col < COLS; ++col) {
        for (int row = 0; row < ROWS; ++row) {
            uint8_t bit = in_stream[col * ROWS + row];
            out_codewords[row] |= (uint8_t)(bit << col);
        }
    }
}

int main(void) {
    /* 1. Вхідне інформаційне повідомлення: 4 блоки по 4 біти */
    uint8_t raw_data[ROWS] = {0b1010, 0b1100, 0b0111, 0b0001};
    uint8_t encoded[ROWS];

    printf("=== 1. Кодування інформаційних блоків ===\n");
    for (int i = 0; i < ROWS; ++i) {
        encoded[i] = hamming_encode_nibble(raw_data[i]);
        printf("Блок %d: дані=0x%X -> кодове слово=0x%02X (7 біт)\n", i, raw_data[i], encoded[i]);
    }

    /* 2. Переміжнення */
    uint8_t channel_stream[ROWS * COLS];
    matrix_interleave(encoded, channel_stream);

    /* 3. Симуляція каналу: накладання пачки помилок із 3 бітів підряд */
    printf("\n=== 2. Передача через канал з пакетом завад ===\n");
    printf("Накладання неперервного пакету з 3 помилок на біти [5, 6, 7]...\n");
    channel_stream[5] ^= 1;
    channel_stream[6] ^= 1;
    channel_stream[7] ^= 1;

    /* 4. Депереміжнення на приймачі */
    uint8_t received_encoded[ROWS];
    matrix_deinterleave(channel_stream, received_encoded);

    /* 5. Декодування зі синдромним виправленням */
    printf("\n=== 3. Депереміжнення та відновлення даних ===\n");
    bool all_recovered = true;
    for (int i = 0; i < ROWS; ++i) {
        bool corrected = false;
        int error_idx = -1;
        uint8_t recovered = hamming_decode_codeword(received_encoded[i], &corrected, &error_idx);
        bool match = (recovered == raw_data[i]);
        if (!match) all_recovered = false;

        printf("Рядок %d: вхід=0x%X, після каналу=0x%02X -> відновлено=0x%X (виправлено біт #%d, збіг: %s)\n",
               i, raw_data[i], received_encoded[i], recovered,
               error_idx, match ? "OK" : "ПОМИЛКА");
    }

    printf("\nПідсумок: %s\n", all_recovered ?
           "УСІ ДАНІ УСПІШНО ВІДНОВЛЕНО ЗАВДЯКИ РОЗСІЮВАННЮ ПАКЕТУ!" :
           "ВТРАТА ДАНИХ: пакет перевищив виправну здатність коду.");

    return 0;
}
