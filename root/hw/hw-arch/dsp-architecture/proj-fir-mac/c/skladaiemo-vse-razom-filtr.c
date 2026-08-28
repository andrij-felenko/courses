#include <stdint.h>

#define N 64                         /* степінь двійки: дешева маска */

static int16_t coef[N];              /* коефіцієнти в Q15, задані наперед */
static int16_t hist[N];              /* кільцевий буфер відліків */
static unsigned pos = 0;             /* беззнаковий → маска замість % */

/* Насичення широкої суми до 16-бітного відліку зі знаком. */
static inline int16_t sat16(int64_t v)
{
    if (v >  32767) return  32767;
    if (v < -32768) return -32768;
    return (int16_t)v;
}

/* Один відлік усередину — один відфільтрований назовні. */
int16_t fir_step(int16_t sample)
{
    hist[pos] = sample;              /* новий відлік затирає найдавніший */

    int64_t acc = 0;                 /* широкий акумулятор (замінює 40 біт DSP) */
    unsigned idx = pos;
    for (int i = 0; i < N; ++i) {
        acc += (int64_t)hist[idx] * coef[i];   /* MAC: множ і накопич */
        idx = (idx - 1) & (N - 1);             /* крок назад по кільцю */
    }

    pos = (pos + 1) & (N - 1);       /* просунути місце запису */
    return sat16(acc >> 15);         /* масштаб Q15 → Q0 + насичення */
}
