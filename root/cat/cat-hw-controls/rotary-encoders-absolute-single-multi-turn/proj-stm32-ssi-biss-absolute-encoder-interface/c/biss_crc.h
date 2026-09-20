#ifndef BISS_CRC_H
#define BISS_CRC_H

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/** Поліном CRC-6 за специфікацією BiSS-C: P(x) = x^6 + x^1 + x^0 (маска 0x03) */
#define BISS_CRC6_POLYNOMIAL 0x03
#define BISS_CRC6_MASK       0x3F

/**
 * @brief Обчислення контрольної суми CRC-6 для послідовності бітів за протоколом BiSS-C
 * @param data Вхідні дані (побітово вирівняні)
 * @param bit_length Кількість бітів даних у телеграмі
 * @return 6-бітна інвертована контрольна сума BiSS CRC
 */
static inline uint8_t biss_crc6_calculate(uint64_t data, uint8_t bit_length) {
    uint8_t crc = 0x00;

    for (int8_t i = (int8_t)bit_length - 1; i >= 0; i--) {
        uint8_t bit = (uint8_t)((data >> i) & 0x01);
        uint8_t crc_msb = (crc >> 5) & 0x01;
        
        crc <<= 1;
        if (crc_msb ^ bit) {
            crc ^= BISS_CRC6_POLYNOMIAL;
        }
        crc &= BISS_CRC6_MASK;
    }

    /* BiSS-C передає інвертований результат CRC */
    return (uint8_t)(~crc & BISS_CRC6_MASK);
}

/**
 * @brief Верифікація контрольної суми кадру BiSS-C
 * @param data Дані кадру без бітів CRC
 * @param bit_length Кількість бітів даних
 * @param expected_crc Отримана з кадру CRC
 * @return true якщо CRC збігається, false якщо виявлено помилку
 */
static inline bool biss_crc6_verify(uint64_t data, uint8_t bit_length, uint8_t expected_crc) {
    uint8_t calculated = biss_crc6_calculate(data, bit_length);
    return (calculated == (expected_crc & BISS_CRC6_MASK));
}

#ifdef __cplusplus
}
#endif

#endif /* BISS_CRC_H */
