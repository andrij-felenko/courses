#include <stdint.h>
#include <stddef.h>

static uint8_t gf_exp[512];   // антилог: gf_exp[i] = αⁱ  (подвоєно, щоб обійтися без % 255)
static uint8_t gf_log[256];   // логарифм: gf_log[αⁱ] = i

void gf_init(void) {
    uint8_t x = 1;                         // α⁰ = 1
    for (int i = 0; i < 255; i++) {
        gf_exp[i] = x;
        gf_log[x] = (uint8_t)i;
        uint8_t hi = x & 0x80;             // чи «вилізе» степінь x⁸ після зсуву
        x <<= 1;                           // множення на α: зсув ліворуч
        if (hi) x ^= 0x1D;                 // переповнення → редукція (0x11D без старшого біта)
    }
    for (int i = 255; i < 512; i++)        // подвоюємо, щоб gf_log[a]+gf_log[b] (до 508) читалося прямо
        gf_exp[i] = gf_exp[i - 255];
    gf_log[0] = 0;                          // 0 не має логарифма; нулі обробляємо окремо
}

static inline uint8_t gf_mul(uint8_t a, uint8_t b) {
    if (a == 0 || b == 0) return 0;
    return gf_exp[gf_log[a] + gf_log[b]];   // αⁱ · αʲ = α^(i+j)
}

static inline uint8_t gf_inv(uint8_t a) {   // a ≠ 0
    return gf_exp[255 - gf_log[a]];          // 1/α^i = α^(255−i), бо α²⁵⁵ = 1
}
