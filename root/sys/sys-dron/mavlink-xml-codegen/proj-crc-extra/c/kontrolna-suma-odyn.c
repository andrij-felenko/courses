#include <stdint.h>
#include <stddef.h>

#define CRC_POLY 0x8408u   /* дзеркальне подання твірного многочлена 0x1021 */
#define CRC_INIT 0xFFFFu

/* CRC-16/MCRF4XX побітно: вісім кроків на кожен байт. */
uint16_t crc16_bitwise(const uint8_t *data, size_t len, uint16_t crc)
{
    for (size_t i = 0; i < len; i++) {
        crc ^= data[i];                        /* байт — у молодші вісім бітів */
        for (int bit = 0; bit < 8; bit++) {
            if (crc & 1u)                      /* вилітлий біт = 1 */
                crc = (uint16_t)((crc >> 1) ^ CRC_POLY);
            else
                crc = (uint16_t)(crc >> 1);
        }
    }
    return crc;
}
