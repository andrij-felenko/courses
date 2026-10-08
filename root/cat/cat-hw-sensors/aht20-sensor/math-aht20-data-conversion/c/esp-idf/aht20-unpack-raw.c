#include <stdint.h>

void aht20_unpack_raw(const uint8_t raw[6], uint32_t *s_rh, uint32_t *s_t) {
    if (!raw || !s_rh || !s_t) return;

    // Розпакування 20-бітного коду відносної вологості
    *s_rh = ((uint32_t)raw[1] << 12) | 
            ((uint32_t)raw[2] << 4)  | 
            ((uint32_t)raw[3] >> 4);

    // Розпакування 20-бітного коду температури
    *s_t = (((uint32_t)raw[3] & 0x0F) << 16) | 
           ((uint32_t)raw[4] << 8)         | 
           (uint32_t)raw[5];
}
