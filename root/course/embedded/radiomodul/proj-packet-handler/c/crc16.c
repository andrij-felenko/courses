#include "crc16.h"

uint16_t crc16_update(uint16_t crc, uint8_t byte)
{
    /* Байт лягає у старшу половину регістра: далі вісім зсувів,
       і на кожному, де виїхала одиниця, домішуємо поліном. */
    crc ^= (uint16_t)((uint16_t)byte << 8);

    for (int i = 0; i < 8; i++) {
        const int msb = (crc & 0x8000u) != 0;
        crc = (uint16_t)(crc << 1);
        if (msb) {
            crc = (uint16_t)(crc ^ CRC16_POLY);
        }
    }
    return crc;
}

uint16_t crc16_block(const uint8_t *data, size_t len)
{
    uint16_t crc = CRC16_INIT;
    for (size_t i = 0; i < len; i++) {
        crc = crc16_update(crc, data[i]);
    }
    return crc;
}
