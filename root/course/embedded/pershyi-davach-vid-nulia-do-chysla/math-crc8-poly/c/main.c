#include <stdio.h>
#include <stdlib.h>

#include "crc8.h"
#include "errscan.h"

/* Ті самі вісім тактів на байт, що й у ручному розрахунку зі статті. */
static void show_manual_example(void)
{
    const uint8_t data[2] = { 0xBE, 0xEF };
    uint8_t reg = (uint8_t)CRC8_INIT;
    uint8_t steps[8];

    printf("Ручний розрахунок кадру 0xBE 0xEF (Init = 0x%02X)\n", (unsigned)CRC8_INIT);
    for (size_t i = 0; i < 2; ++i) {
        printf("  байт 0x%02X: змішування 0x%02X ^ 0x%02X = 0x%02X\n",
               data[i], reg, data[i], (uint8_t)(reg ^ data[i]));
        reg = crc8_byte_trace(reg, data[i], steps);
        printf("    такти:");
        for (int b = 0; b < 8; ++b) {
            printf(" 0x%02X", steps[b]);
        }
        printf("\n    залишок після байта: 0x%02X\n", reg);
    }
    printf("  CRC-8 = 0x%02X\n\n", reg);
}

static void show_table_head(void)
{
    const uint8_t *table = crc8_table();

    printf("Перші 16 елементів таблиці на 256 байтів:\n ");
    for (int i = 0; i < 16; ++i) {
        printf(" 0x%02X", table[i]);
    }
    printf("\n\n");
}

/* Три класи помилок, які арифметична сума не бачить принципово. */
static void show_checksum_holes(void)
{
    const uint8_t comp[2] = { 0xBF, 0xEE }; /* +1 у першому байті, -1 у другому */
    const uint8_t orig[2] = { 0xBE, 0xEF };
    const uint8_t zeroed[3] = { 0xBE, 0x00, 0xEF };
    uint8_t sum_ab, sum_ba, crc_ab, crc_ba;

    errscan_swap_demo(0xBEEF, &sum_ab, &sum_ba, &crc_ab, &crc_ba);
    printf("Переставлені байти: сума 0x%02X проти 0x%02X, CRC 0x%02X проти 0x%02X\n",
           sum_ab, sum_ba, crc_ab, crc_ba);
    printf("Компенсовані біти:  сума 0x%02X проти 0x%02X, CRC 0x%02X проти 0x%02X\n",
           checksum8(orig, 2), checksum8(comp, 2),
           crc8_fast(orig, 2), crc8_fast(comp, 2));
    printf("Вставлений 0x00:    сума 0x%02X проти 0x%02X, CRC 0x%02X проти 0x%02X\n\n",
           checksum8(orig, 2), checksum8(zeroed, 3),
           crc8_fast(orig, 2), crc8_fast(zeroed, 3));
}

static void show_error_scan(void)
{
    static const uint16_t words[] = { 0xBEEF, 0x0000, 0xFFFF, 0x1234 };

    printf("Пропущені спотворення кадру (дані + байт захисту, 24 біти):\n");
    printf("  слово   вид помилки       перевірено   повз CRC   повз суму\n");
    for (size_t i = 0; i < sizeof words / sizeof words[0]; ++i) {
        for (int bits = 1; bits <= 3; ++bits) {
            const errscan_stats st = errscan_flips(words[i], bits);
            printf("  0x%04X  %d-бітові        %10lu %10lu %11lu\n",
                   words[i], bits, st.checked, st.missed_crc, st.missed_sum);
        }
        {
            const errscan_stats st = errscan_bursts(words[i], 8);
            printf("  0x%04X  пакети до 8 біт %10lu %10lu %11lu\n",
                   words[i], st.checked, st.missed_crc, st.missed_sum);
        }
    }
    printf("\n");
}

/* Самоперевірка: контрольні значення з даташита, збіг двох реалізацій
   на всіх 65536 кадрах і поведінка на вироджених входах. */
static int self_test(void)
{
    /* Рядок "123456789" — стандартний контрольний вектор для цього полінома. */
    static const uint8_t check[9] = { 0x31, 0x32, 0x33, 0x34, 0x35,
                                      0x36, 0x37, 0x38, 0x39 };
    const uint8_t sample[2] = { 0xBE, 0xEF };
    uint8_t frame[3] = { 0xBE, 0xEF, 0x92 };
    uint16_t value = 0;
    int bad = 0;

    if (crc8_fast(check, sizeof check) != 0xF7u) {
        printf("ПОМИЛКА: контрольний вектор дав 0x%02X замість 0xF7\n",
               crc8_fast(check, sizeof check));
        bad++;
    }
    if (crc8_fast(sample, 2) != 0x92u) {
        printf("ПОМИЛКА: кадр 0xBE 0xEF дав 0x%02X замість 0x92\n",
               crc8_fast(sample, 2));
        bad++;
    }
    for (unsigned w = 0; w < 65536u; ++w) {
        const uint8_t d[2] = { (uint8_t)(w >> 8), (uint8_t)w };
        if (crc8_fast(d, 2) != crc8_bitwise(d, 2)) {
            printf("ПОМИЛКА: таблиця розійшлася з автоматом на 0x%04X\n", w);
            bad++;
            break;
        }
    }
    if (!crc8_frame_ok(frame, 3)) {
        printf("ПОМИЛКА: цілий кадр не пройшов перевірку\n");
        bad++;
    }
    if (crc8_sht3x_word(frame, 3, &value) != 0 || value != 0xBEEFu) {
        printf("ПОМИЛКА: слово розібрано як 0x%04X\n", value);
        bad++;
    }
    frame[1] ^= 0x01u; /* один спотворений біт даних */
    if (crc8_frame_ok(frame, 3) || crc8_sht3x_word(frame, 3, &value) == 0) {
        printf("ПОМИЛКА: битий кадр прийнято\n");
        bad++;
    }
    if (crc8_frame_ok(NULL, 3) || crc8_frame_ok(frame, 1) ||
        crc8_sht3x_word(frame, 2, &value) == 0 ||
        crc8_sht3x_word(frame, 3, NULL) == 0) {
        printf("ПОМИЛКА: вироджений вхід не відкинуто\n");
        bad++;
    }
    return bad;
}

int main(void)
{
    show_manual_example();
    show_table_head();
    show_checksum_holes();
    show_error_scan();

    if (self_test() != 0) {
        return EXIT_FAILURE;
    }
    printf("Самоперевірка пройдена.\n");
    return EXIT_SUCCESS;
}
