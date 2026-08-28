#include <stdint.h>
#include <string.h>

void put_u32_be(uint8_t *buf, size_t off, uint32_t v) {   // ціле — зсувами
    buf[off + 0] = (v >> 24) & 0xFF;       // старший байт — першим (big-endian)
    buf[off + 1] = (v >> 16) & 0xFF;
    buf[off + 2] = (v >>  8) & 0xFF;
    buf[off + 3] = (v >>  0) & 0xFF;
}

uint32_t get_u32_be(const uint8_t *buf, size_t off) {     // дзеркально: збираємо назад
    return ((uint32_t)buf[off + 0] << 24) | ((uint32_t)buf[off + 1] << 16)
         | ((uint32_t)buf[off + 2] <<  8) |  (uint32_t)buf[off + 3];
}

void put_f32_be(uint8_t *buf, size_t off, float f) {      // float — через байти, не зсувом
    uint8_t tmp[4];
    memcpy(tmp, &f, 4);                     // дістали байти IEEE-754, не чіпаючи бітів
    // tmp лежить у ПОРЯДКУ ПАМ'ЯТІ машини → вирівнюємо до мережевого:
    const uint16_t probe = 1;
    if (*(const uint8_t *)&probe) {         // молодший байт першим → little-endian
        for (int i = 0; i < 2; i++) {       // 4 байти задом наперед
            uint8_t t = tmp[i]; tmp[i] = tmp[3 - i]; tmp[3 - i] = t;
        }
    }
    memcpy(buf + off, tmp, 4);
}
