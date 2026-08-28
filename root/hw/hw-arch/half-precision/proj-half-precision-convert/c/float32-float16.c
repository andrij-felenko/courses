#include <stdint.h>
#include <string.h>

// float32 -> float16 (IEEE 754 binary16) з округленням до найближчого-парного,
// обробкою ∞/NaN, переповнення під стелю 65504, денормалей і зникнення до нуля.
uint16_t f32_to_f16(float x) {
    uint32_t bits;
    memcpy(&bits, &x, sizeof bits);

    uint32_t sign = (bits >> 16) & 0x8000u;   // знак одразу на місце в 16-бітному слові
    uint32_t rest = bits & 0x7FFFFFFFu;        // усе, крім знаку

    // --- ∞ і NaN: порядок float32 = усі одиниці (rest >= 0x7F800000) ---
    if (rest >= 0x7F800000u) {
        if (rest > 0x7F800000u) {              // мантиса ≠ 0 → NaN
            uint16_t m = (uint16_t)(rest >> 13) & 0x03FFu;  // урізаємо мантису до 10 бітів
            if (m == 0u) m = 0x0200u;          // не дати їй стати ∞: лишаємо quiet-біт
            return (uint16_t)(sign | 0x7C00u | m);
        }
        return (uint16_t)(sign | 0x7C00u);     // ∞  (0x7C00 = порядок float16 усі одиниці)
    }

    // --- звичайне число: перерахунок порядку зі зсуву 127 у зсув 15 ---
    int32_t e = (int32_t)(rest >> 23) - 127 + 15;

    // Переповнення під стелю: порядок float16 не вміщає → ∞.
    if (e >= 0x1F) {
        return (uint16_t)(sign | 0x7C00u);     // усе, що більше за 65504, стає ∞
    }

    uint32_t mant = rest & 0x007FFFFFu;         // 23 біти мантиси float32

    // --- денормаль float16 або зникнення до нуля (порядок вийшов ≤ 0) ---
    if (e <= 0) {
        if (e < -10) return (uint16_t)sign;     // надто мале навіть для денормалі → ±0
        mant |= 0x00800000u;                    // повертаємо неявну старшу одиницю
        int32_t shift = 14 - e;                 // на скільки зсунути, щоб лягло в денормаль
        uint32_t half = 1u << (shift - 1);
        uint32_t m    = mant >> shift;
        uint32_t rem  = mant & ((1u << shift) - 1u);
        // округлення до найближчого-парного
        if (rem > half || (rem == half && (m & 1u))) m += 1u;
        return (uint16_t)(sign | m);            // переповнення денормалі в нормаль вийде саме
    }

    // --- нормальне число: 10 бітів мантиси + округлення до найближчого-парного ---
    uint32_t m   = mant >> 13;                  // лишаємо старші 10 з 23 бітів
    uint32_t rem = mant & 0x1FFFu;              // 13 відкиданих бітів
    uint16_t out = (uint16_t)(sign | ((uint32_t)e << 10) | m);
    if (rem > 0x1000u || (rem == 0x1000u && (m & 1u))) out += 1u;  // переніс сам підніме порядок
    return out;
}
