#include "sf_crc32.h"

/* Таблиця на пів-байт: 16 входів = 64 байти проти кілобайта повної
 * таблиці на 256 входів. Для вузла, у якого весь код живе в 64 КіБ
 * флешу, це той компроміс, який роблять у житті: удвічі більше зсувів
 * на байт, зате таблиця не з'їдає цілий сектор програмної пам'яті.
 * Значення — стандартні для полінома 0xEDB88320. */
static const uint32_t sf_crc32_nibble[16] = {
    0x00000000u, 0x1DB71064u, 0x3B6E20C8u, 0x26D930ACu,
    0x76DC4190u, 0x6B6B51F4u, 0x4DB26158u, 0x5005713Cu,
    0xEDB88320u, 0xF00F9344u, 0xD6D6A3E8u, 0xCB61B38Cu,
    0x9B64C2B0u, 0x86D3D2D4u, 0xA00AE278u, 0xBDBDF21Cu,
};

uint32_t sf_crc32_update(uint32_t crc, const void *data, size_t len)
{
    const uint8_t *p = (const uint8_t *)data;

    while (len--) {
        crc ^= (uint32_t)(*p++);
        crc = (crc >> 4) ^ sf_crc32_nibble[crc & 0x0Fu];
        crc = (crc >> 4) ^ sf_crc32_nibble[crc & 0x0Fu];
    }
    return crc;
}

uint32_t sf_crc32_final(uint32_t crc)
{
    return crc ^ 0xFFFFFFFFu;
}

uint32_t sf_crc32(const void *data, size_t len)
{
    return sf_crc32_final(sf_crc32_update(SF_CRC32_INIT, data, len));
}
