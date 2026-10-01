#include <stdint.h>
#include <stddef.h>

/**
 * @brief Обчислення контрольної суми CRC-8 для кадру AHT20 (попобітовий алгоритм).
 * @param data Вказівник на масив сирих байтів кадру.
 * @param len Кількість байтів у масиві.
 * @return Восьмибітова контрольна сума CRC-8.
 */
uint8_t aht20_crc8_bitwise(const uint8_t *data, size_t len) {
    uint8_t crc = 0xFF; /* Вектор ініціалізації */
    
    for (size_t i = 0; i < len; i++) {
        crc ^= data[i];
        for (uint8_t bit = 0; bit < 8; bit++) {
            if ((crc & 0x80) != 0) {
                crc = (uint8_t)((crc << 1) ^ 0x31);
            } else {
                crc = (uint8_t)(crc << 1);
            }
        }
    }
    return crc;
}
