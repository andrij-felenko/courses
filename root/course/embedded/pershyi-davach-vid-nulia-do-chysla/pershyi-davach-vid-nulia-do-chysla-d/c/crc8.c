#include "crc8.h"

uint8_t sht3x_crc8(const uint8_t *data, size_t len)
{
    uint8_t crc = SHT3X_CRC8_INIT;

    if (data == NULL) {
        return crc;
    }

    for (size_t i = 0; i < len; ++i) {
        /* Черговий байт замішується в регістр: це те саме, що подати
           його біти на вхід зсувного регістра зі зворотними зв'язками. */
        crc ^= data[i];

        for (int bit = 0; bit < 8; ++bit) {
            if ((crc & 0x80u) != 0u) {
                /* Старший розряд вилітає з регістра — віднімаємо (XOR) поліном. */
                crc = (uint8_t)((uint8_t)(crc << 1) ^ SHT3X_CRC8_POLYNOMIAL);
            } else {
                crc = (uint8_t)(crc << 1);
            }
        }
    }

    return crc;
}

bool sht3x_crc8_check(const uint8_t word[2], uint8_t expected)
{
    if (word == NULL) {
        return false;
    }
    /* Перевірочне слово з даташиту: 0xBE 0xEF дає CRC 0x92. */
    return sht3x_crc8(word, 2u) == expected;
}
