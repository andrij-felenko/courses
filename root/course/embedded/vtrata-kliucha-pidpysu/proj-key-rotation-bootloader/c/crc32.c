#include "crc32.h"

/*
 * Побітова версія без таблиці: 1 КБ таблиці у завантажувачі коштує дорожче,
 * ніж вісім зсувів на байт — заголовок маніфесту має 152 байти, сторінка стану 32.
 */
uint32_t crc32_ieee(const uint8_t *data, size_t length)
{
    uint32_t crc = 0xFFFFFFFFU;

    for (size_t i = 0; i < length; ++i) {
        crc ^= (uint32_t)data[i];
        for (int bit = 0; bit < 8; ++bit) {
            uint32_t mask = (uint32_t)-(int32_t)(crc & 1U);
            crc = (crc >> 1) ^ (0xEDB88320U & mask);
        }
    }

    return ~crc;
}
