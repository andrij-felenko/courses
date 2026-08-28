#include <stdint.h>

/* Стани кодуємо числами 0..3 — це індекс у таблиці δ.
   next[state][bit] — наступний стан; точно як таблиця вище. */
static const uint8_t next[4][2] = {
    /*        bit=0  bit=1 */
    /* S0 */ {  0,     1  },
    /* S1 */ {  2,     1  },
    /* S2 */ {  0,     3  },
    /* S3 */ {  2,     1  },
};

int has_101(const uint8_t *in, int n)
{
    uint8_t s = 0;                 /* q0 = S0 */
    for (int i = 0; i < n; i++) {
        s = next[s][in[i] & 1];    /* один перехід на символ: δ(s, біт) */
        if (s == 3)                /* S3 ∈ F — підрядок знайдено */
            return 1;
    }
    return 0;
}
