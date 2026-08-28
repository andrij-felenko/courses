#include <stdint.h>
#include <string.h>
#include <math.h>

// Дістати з float три поля IEEE 754 single і зібрати значення назад.
float decode_f32(float x) {
    uint32_t bits;
    memcpy(&bits, &x, sizeof bits);        // біти float як ціле — без UB

    uint32_t s    =  bits >> 31;           // 1 біт знаку (позиція 31)
    uint32_t exp  = (bits >> 23) & 0xFF;   // 8 бітів порядку (30..23)
    uint32_t mant =  bits & 0x7FFFFF;      // 23 біти мантиси (22..0)

    // −3.5f → s = 1, exp = 128, mant = 0x600000 (двійкове 110...0)
    float sign = (s ? -1.0f : 1.0f);
    float frac = 1.0f + (float)mant / 0x800000;   // прихована 1 + дріб/2^23
    return sign * frac * ldexpf(1.0f, (int)exp - 127);   // × 2^(exp−127)
}
