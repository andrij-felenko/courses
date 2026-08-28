#include <stdint.h>
#include <stdio.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

#define TAPS 64                 /* довжина КІХ: 64 відводи */

typedef int16_t q15_t;          /* Q1.15: ціле v ↔ дійсне v / 2¹⁵, діапазон [−1, +1) */

typedef struct {
    q15_t h[TAPS];              /* коефіцієнти ФНЧ у Q15 */
    q15_t buf[TAPS];            /* кільцевий буфер останніх TAPS входів */
    int   widx;                 /* куди писати наступний вхід */
    int   phase;                /* лічильник фази: 0 … M−1 */
    int   M;                    /* коефіцієнт проріджування */
} decim_t;

static q15_t to_q15(double v)   /* дійсне [−1, +1) → ціле Q15 із насиченням */
{
    long r = lround(v * 32768.0);          /* 2¹⁵ = 32768 */
    if (r >  32767) r =  32767;             /* +1.0 у 16 бітах не подати */
    if (r < -32768) r = -32768;
    return (q15_t)r;
}

/* Скласти проріджувач: коефіцієнти ФНЧ зі зрізом fs/(2M) — віконний sinc
   із вікном Геммінга, унормований до одиничного підсилення на 0 Гц. */
void decim_init(decim_t *d, int M)
{
    const int    N  = TAPS;
    const double fc = 0.5 / (double)M;      /* зріз, нормований до fs: 1/(2M) */
    double taps[TAPS], sum = 0.0;
    int k;

    for (k = 0; k < N; k++) {
        double m    = (double)k - (N - 1) / 2.0;                     /* центр вікна */
        double sinc = (fabs(m) < 1e-9) ? 2.0 * fc
                                       : sin(2.0 * M_PI * fc * m) / (M_PI * m);
        double win  = 0.54 - 0.46 * cos(2.0 * M_PI * k / (N - 1));   /* Геммінг */
        taps[k] = sinc * win;
        sum += taps[k];
    }
    for (k = 0; k < N; k++)
        d->h[k] = to_q15(taps[k] / sum);    /* Σh = 1 → підсилення 1 на 0 Гц */

    for (k = 0; k < N; k++) d->buf[k] = 0;  /* розігрів: буфер стартує з нулів */
    d->widx  = 0;
    d->phase = 0;
    d->M     = M;
}
