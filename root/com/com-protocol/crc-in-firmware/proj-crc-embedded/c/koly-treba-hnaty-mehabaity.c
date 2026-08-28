#include <string.h>

extern const uint32_t crc32_slice[4][256];   /* 4 КБ у флеші; crc32_slice[0] — байтова таблиця */

uint32_t crc32_update_fast(uint32_t crc, const uint8_t *p, size_t n) {
    while (n >= 4) {
        uint32_t w;
        memcpy(&w, p, 4);                    /* безпечне завантаження слова */
        crc ^= w;                            /* little-endian: молодший байт слова — перший */
        crc = crc32_slice[3][ crc        & 0xFF]
            ^ crc32_slice[2][(crc >>  8) & 0xFF]
            ^ crc32_slice[1][(crc >> 16) & 0xFF]
            ^ crc32_slice[0][(crc >> 24) & 0xFF];
        p += 4;
        n -= 4;
    }
    while (n--) {                            /* хвіст — звичайним байтовим ядром */
        uint8_t idx = (uint8_t)(crc ^ *p++);
        crc = (crc >> 8) ^ crc32_slice[0][idx];
    }
    return crc;
}
