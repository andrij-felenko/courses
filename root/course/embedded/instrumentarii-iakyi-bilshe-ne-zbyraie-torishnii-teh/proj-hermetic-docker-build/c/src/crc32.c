#include "crc32.h"

/* Півбайтова таблиця полінома 0xEDB88320: кожен байт проходить два кроки */
static const uint32_t k_nibble[16] = {
    0x00000000U, 0x1DB71064U, 0x3B6E20C8U, 0x26D930ACU,
    0x76DC4190U, 0x6B6B51F4U, 0x4DB26158U, 0x5005713CU,
    0xEDB88320U, 0xF00F9344U, 0xD6D6A3E8U, 0xCB61B38CU,
    0x9B64C2B0U, 0x86D3D2D4U, 0xA00AE278U, 0xBDBDF21CU
};

uint32_t crc32_update(uint32_t crc, const void *data, size_t len)
{
    if (data == NULL || len == 0U) {
        return crc;
    }

    const uint8_t *p = (const uint8_t *)data;
    for (size_t i = 0U; i < len; ++i) {
        const uint8_t b = p[i];
        crc = k_nibble[(crc ^ (uint32_t)b) & 0x0FU] ^ (crc >> 4);
        crc = k_nibble[(crc ^ ((uint32_t)b >> 4)) & 0x0FU] ^ (crc >> 4);
    }
    return crc;
}
