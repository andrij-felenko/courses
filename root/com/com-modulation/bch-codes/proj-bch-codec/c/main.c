#include <stdint.h>
/* g(x)=x⁸+x⁷+x⁶+x⁴+1; молодші 8 біт (без x⁸) = 0xD1 = 0b11010001 — це відводи. */
uint8_t bch_parity(const uint8_t data[7])   /* data[0] = біт при x¹⁴ */
{
    uint8_t reg = 0;
    for (int i = 0; i < 7; i++) {            /* k = 7 тактів, старший біт першим */
        uint8_t fb = data[i] ^ (reg >> 7);   /* зворотний зв'язок = вхід ⊕ b₇ */
        reg <<= 1;                           /* зсув bᵢ → bᵢ₊₁, b₇ виходить */
        if (fb & 1) reg ^= 0xD1;             /* відводи там, де g має 1 */
    }
    return reg;                              /* 8 контрольних бітів: b₇…b₀ = x⁷…x⁰ */
}
