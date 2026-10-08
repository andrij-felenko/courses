#include <stdint.h>
#include <stdbool.h>

// Обчислення контрольної суми CRC-8 за специфікацією Sensirion (поліном 0x31, ініціалізація 0xFF)
uint8_t sht30_calc_crc8(const uint8_t *data, size_t len) {
    uint8_t crc = 0xFF;
    for (size_t i = 0; i < len; i++) {
        crc ^= data[i];
        for (uint8_t bit = 8; bit > 0; --bit) {
            if (crc & 0x80) {
                crc = (crc << 1) ^ 0x31;
            } else {
                crc = (crc << 1);
            }
        }
    }
    return crc;
}

// Перетворення 6-байтового масиву від SHT30 у фізичні значення температури та вологості
bool sht30_decode_data(const uint8_t raw[6], float *temperature_c, float *humidity_rh) {
    // Валідація контрольної суми CRC-8 для блоку температури
    if (sht30_calc_crc8(&raw[0], 2) != raw[2]) {
        return false;
    }
    // Валідація контрольної суми CRC-8 для блоку вологості
    if (sht30_calc_crc8(&raw[3], 2) != raw[5]) {
        return false;
    }

    // Збирання 16-бітних кодових значень АЦП
    uint16_t raw_temp = ((uint16_t)raw[0] << 8) | raw[1];
    uint16_t raw_humi = ((uint16_t)raw[3] << 8) | raw[4];

    // Обчислення за формулами Sensirion
    *temperature_c = -45.0f + 175.0f * ((float)raw_temp / 65535.0f);
    *humidity_rh = 100.0f * ((float)raw_humi / 65535.0f);

    return true;
}
