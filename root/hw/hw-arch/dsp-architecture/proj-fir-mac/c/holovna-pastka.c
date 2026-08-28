#include <stdint.h>

#define N 64

static int16_t coef[N];
static int16_t hist[N];
static int      pos = 0;

int16_t fir_wide(int16_t sample)
{
    hist[pos] = sample;

    int64_t acc = 0;                          /* широкий акумулятор */
    int     idx = pos;
    for (int i = 0; i < N; ++i) {
        acc += (int64_t)hist[idx] * coef[i];  /* добуток одразу в 64 біт */
        idx = (idx == 0) ? (N - 1) : (idx - 1);
    }

    acc >>= 15;                               /* Q15 → Q0 */

    pos = (pos == N - 1) ? 0 : (pos + 1);
    return sat16(acc);                        /* насичення на виході — далі */
}
