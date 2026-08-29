#ifndef ERRSCAN_H
#define ERRSCAN_H

#include <stddef.h>
#include <stdint.h>

/* Скільки спотворень перебрано і скільки з них пройшло повз кожен із кодів.
   Кадр — два байти даних плюс байт захисту, тобто 24 біти. */
typedef struct {
    unsigned long checked;
    unsigned long missed_crc;
    unsigned long missed_sum;
} errscan_stats;

/* Арифметична контрольна сума: додавання байтів за модулем 256. */
uint8_t checksum8(const uint8_t *data, size_t len);

/* Перебирає всі комбінації рівно bits інвертованих бітів кадру. */
errscan_stats errscan_flips(uint16_t word, int bits);

/* Перебирає всі пакетні помилки довжиною від 1 до max_len:
   крайні біти вікна інвертовані обов'язково, внутрішні — у всіх варіантах. */
errscan_stats errscan_bursts(uint16_t word, int max_len);

/* Дві однакові пари байтів під двома кодами: одна із CRC-8, друга з сумою. */
void errscan_swap_demo(uint16_t word, uint8_t *sum_ab, uint8_t *sum_ba,
                       uint8_t *crc_ab, uint8_t *crc_ba);

#endif /* ERRSCAN_H */
