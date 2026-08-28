#include <math.h>
#include <stddef.h>

#ifndef M_PI                        /* у стандарті C його немає — підстрахуймося */
#define M_PI 3.14159265358979323846
#endif

/* FFT «на місці»; n — степінь двійки. На вході re[] — відліки, im[] — нулі,
   на виході re[k], im[k] — комплексний спектр.                              */
void fft_radix2(float *re, float *im, size_t n)
{
    /* 1. перестановка за оберненими бітами: те, що алгоритм ділить
          на парні й непарні, після неї лежить поруч                */
    for (size_t i = 1, j = 0; i < n; i++) {
        size_t bit = n >> 1;
        for (; j & bit; bit >>= 1)
            j ^= bit;
        j ^= bit;
        if (i < j) {
            float t;
            t = re[i]; re[i] = re[j]; re[j] = t;
            t = im[i]; im[i] = im[j]; im[j] = t;
        }
    }
    /* 2. log2(n) ярусів метеликів: пара входів -> пара виходів */
    for (size_t len = 2; len <= n; len <<= 1) {
        float ang = -2.0f * (float)M_PI / (float)len;
        float sr = cosf(ang), si = sinf(ang);        /* крок повороту */
        for (size_t i = 0; i < n; i += len) {
            float wr = 1.0f, wi = 0.0f;              /* множник повороту */
            for (size_t k = 0; k < len / 2; k++) {
                size_t p = i + k, q = p + len / 2;
                float ur = re[p], ui = im[p];
                float vr = re[q]*wr - im[q]*wi;
                float vi = re[q]*wi + im[q]*wr;
                re[p] = ur + vr;  im[p] = ui + vi;
                re[q] = ur - vr;  im[q] = ui - vi;
                float t = wr*sr - wi*si;             /* докрутити множник */
                wi = wr*si + wi*sr;
                wr = t;
            }
        }
    }
}
