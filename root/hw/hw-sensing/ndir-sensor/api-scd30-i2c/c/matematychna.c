#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#define SCD30_CRC8_POLYNOMIAL  0x31
#define SCD30_CRC8_INIT        0xFF

/**
 * @brief Розрахунок контрольної суми CRC-8 за алгоритмом Sensirion.
 * @param data Вказівник на буфер даних (зазвичай 2 байти 16-бітного слова).
 * @param len Кількість байтів для розрахунку.
 * @return 8-бітне значення контрольної суми.
 */
uint8_t scd30_compute_crc8(const uint8_t *data, size_t len) {
    uint8_t crc = SCD30_CRC8_INIT;
    for (size_t i = 0; i < len; ++i) {
        crc ^= data[i];
        for (uint8_t bit = 8; bit > 0; --bit) {
            if (crc & 0x80) {
                crc = (crc << 1) ^ SCD30_CRC8_POLYNOMIAL;
            } else {
                crc = (crc << 1);
            }
        }
    }
    return crc;
}

/**
 * @brief Перевірка цілісності двох байтів даних за допомогою отриманого CRC.
 */
bool scd30_check_crc8(const uint8_t data[2], uint8_t expected_crc) {
    return scd30_compute_crc8(data, 2) == expected_crc;
}
