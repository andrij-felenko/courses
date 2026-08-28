#include <stdint.h>

#define N 64                 /* кількість коефіцієнтів (порядок фільтра) */

static int16_t coef[N];      /* коефіцієнти h₀…h_{N-1}, задані наперед */
static int16_t hist[N];      /* останні N відліків, hist[0] — найновіший */

/* Наївно: зсунути історію й порахувати згортку в лоба. */
int16_t fir_naive(int16_t sample)
{
    /* зсув вікна: усе на комірку вправо, найдавніший випадає */
    for (int i = N - 1; i > 0; --i)
        hist[i] = hist[i - 1];
    hist[0] = sample;                 /* новий відлік — на початок */

    int32_t acc = 0;
    for (int i = 0; i < N; ++i)
        acc += (int32_t)hist[i] * coef[i];

    return (int16_t)(acc >> 15);      /* масштаб Q15 → Q0, про це нижче */
}
