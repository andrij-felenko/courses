#include <stdint.h>

#define N 64

static int16_t coef[N];
static int16_t hist[N];
static int      pos = 0;          /* куди покласти наступний відлік */

int16_t fir_ring(int16_t sample)
{
    hist[pos] = sample;           /* новий відлік затер найдавніший */

    int32_t acc = 0;
    int     idx = pos;            /* ідемо від найновішого назад у часі */
    for (int i = 0; i < N; ++i) {
        acc += (int32_t)hist[idx] * coef[i];
        idx = (idx == 0) ? (N - 1) : (idx - 1);   /* крок назад по кільцю */
    }

    pos = (pos == N - 1) ? 0 : (pos + 1);         /* просунути місце запису */
    return (int16_t)(acc >> 15);
}
