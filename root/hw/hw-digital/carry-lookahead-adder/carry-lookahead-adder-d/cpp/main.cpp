#include <stdint.h>
#include <stdio.h>

// 4-розрядний прискорений суматор: переноси рахуємо ПРЯМО з G, P, C0.
// Повертає 4-бітну суму; через c4 віддає перенос-вихід групи.
uint8_t cla4(uint8_t a, uint8_t b, uint8_t c0, uint8_t *c4) {
    uint8_t g[4], p[4];
    for (int i = 0; i < 4; i++) {
        uint8_t ai = (a >> i) & 1, bi = (b >> i) & 1;
        g[i] = ai & bi;          // породжує: обидва біти 1
        p[i] = ai ^ bi;          // пропускає: рівно один біт 1
    }
    // переноси — кожен прямою формулою, БЕЗ посилання на сусідній перенос
    uint8_t c1 = g[0] | (p[0] & c0);
    uint8_t c2 = g[1] | (p[1] & g[0]) | (p[1] & p[0] & c0);
    uint8_t c3 = g[2] | (p[2] & g[1]) | (p[2] & p[1] & g[0]) | (p[2] & p[1] & p[0] & c0);
    *c4       = g[3] | (p[3] & g[2]) | (p[3] & p[2] & g[1])
                     | (p[3] & p[2] & p[1] & g[0]) | (p[3] & p[2] & p[1] & p[0] & c0);

    uint8_t cin[4] = { c0, c1, c2, c3 };
    uint8_t sum = 0;
    for (int i = 0; i < 4; i++)
        sum |= (uint8_t)((p[i] ^ cin[i]) << i);   // Sᵢ = Pᵢ ⊕ Cᵢ
    return sum;
}

int main(void) {
    uint8_t c4;
    uint8_t s = cla4(0x0B, 0x06, 0, &c4);          // 1011 + 0110 = 11 + 6
    printf("sum = %u, carry-out = %u\n", s, c4);   // sum = 1, carry-out = 1  →  1 0001 = 17
}
