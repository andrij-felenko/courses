#include <math.h>
#define N    73                  /* число відводів (непарне → симетрія) */
#define FS   16000.0f            /* частота дискретизації, Гц */
#define FC   3700.0f             /* центр переходу: (3400+4000)/2 */

float b[N];                      /* сюди ляжуть коефіцієнти */

void design_lpf(void)
{
    const int   M  = N - 1;                 /* порядок */
    const float wc = 2.0f * (float)M_PI * (FC / FS);   /* норм. частота зрізу */
    float sum = 0.0f;

    for (int k = 0; k <= M; k++) {
        int n = k - M / 2;                  /* симетрично навколо центру */

        /* 1) ідеальний sinc (з границею sin(0)/0 = 1 у центрі) */
        float ideal = (n == 0) ? (wc / (float)M_PI)
                               : sinf(wc * n) / ((float)M_PI * n);

        /* 2) вікно Геммінга — м'яко гасить краї */
        float win = 0.54f - 0.46f * cosf(2.0f * (float)M_PI * k / M);

        b[k] = ideal * win;                 /* 3) завіконений відвід */
        sum += b[k];
    }

    /* 4) нормування: підсилення на постійному струмі = 1 (сума ваг = 1) */
    for (int k = 0; k <= N - 1; k++)
        b[k] /= sum;
}
