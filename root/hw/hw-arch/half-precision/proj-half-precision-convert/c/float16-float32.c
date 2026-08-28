#include <stdint.h>
#include <string.h>

// float16 -> float32. Денормаль float16 стає НОРМАЛЬНИМ float32 (треба нормалізувати).
float f16_to_f32(uint16_t h) {
    uint32_t sign = (uint32_t)(h & 0x8000u) << 16;   // знак на місце float32
    uint32_t exp  = (h >> 10) & 0x1Fu;               // 5 бітів порядку
    uint32_t mant = h & 0x03FFu;                      // 10 бітів мантиси
    uint32_t bits;

    if (exp == 0u) {                                 // порядок 0: нуль або денормаль
        if (mant == 0u) {
            bits = sign;                             // ±0
        } else {
            // денормаль float16 → нормаль float32: зсуваємо мантису, доки
            // неявна одиниця (біт 0x0400) не «випливе», рахуючи зсуви в порядку.
            exp = 1u;
            while ((mant & 0x0400u) == 0u) { mant <<= 1; exp--; }
            mant &= 0x03FFu;                         // прибрати неявну одиницю
            bits = sign | ((exp - 15u + 127u) << 23) | (mant << 13);
        }
    } else if (exp == 0x1Fu) {                       // порядок усі одиниці: ∞ або NaN
        bits = sign | 0x7F800000u | (mant << 13);    // мантиса 0 → ∞; ≠0 → NaN (payload зберігся)
    } else {                                         // нормальне число
        bits = sign | ((exp - 15u + 127u) << 23) | (mant << 13);
    }

    float x;
    memcpy(&x, &bits, sizeof x);
    return x;
}
