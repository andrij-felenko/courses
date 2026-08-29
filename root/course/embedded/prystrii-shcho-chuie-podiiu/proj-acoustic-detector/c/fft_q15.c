#include "fft_q15.h"

/* Чверть періоду синуса: sin(2π·k/512) у Q15, k = 0…128 (258 байтів Flash).
 * Решту трьох чвертей дістаємо симетрією — тримати повний період означало б
 * витратити кілограм Flash на дані, які й так виводяться двома порівняннями. */
static const int16_t SIN_Q15_QUARTER[129] = {
        0,    402,    804,   1206,   1608,   2009,   2411,   2811,
     3212,   3612,   4011,   4410,   4808,   5205,   5602,   5998,
     6393,   6787,   7180,   7571,   7962,   8351,   8740,   9127,
     9512,   9896,  10279,  10660,  11039,  11417,  11793,  12167,
    12540,  12910,  13279,  13646,  14010,  14373,  14733,  15091,
    15447,  15800,  16151,  16500,  16846,  17190,  17531,  17869,
    18205,  18538,  18868,  19195,  19520,  19841,  20160,  20475,
    20788,  21097,  21403,  21706,  22006,  22302,  22595,  22884,
    23170,  23453,  23732,  24008,  24279,  24548,  24812,  25073,
    25330,  25583,  25833,  26078,  26320,  26557,  26791,  27020,
    27246,  27467,  27684,  27897,  28106,  28311,  28511,  28707,
    28899,  29086,  29269,  29448,  29622,  29792,  29957,  30118,
    30274,  30425,  30572,  30715,  30853,  30986,  31114,  31238,
    31357,  31471,  31581,  31686,  31786,  31881,  31972,  32058,
    32138,  32214,  32286,  32352,  32413,  32470,  32522,  32568,
    32610,  32647,  32679,  32706,  32729,  32746,  32758,  32766,
    32767
};

/* sin(2π·idx/512), idx = 0…511. */
static int16_t sin_q15(unsigned idx)
{
    idx &= (AED_FFT_SIZE - 1);
    if (idx <= 128u) {
        return SIN_Q15_QUARTER[idx];
    }
    if (idx <= 256u) {
        return SIN_Q15_QUARTER[256u - idx];
    }
    if (idx <= 384u) {
        return (int16_t)(-SIN_Q15_QUARTER[idx - 256u]);
    }
    return (int16_t)(-SIN_Q15_QUARTER[512u - idx]);
}

/* cos(x) = sin(x + π/2), тобто зсув на чверть таблиці. */
static int16_t cos_q15(unsigned idx)
{
    return sin_q15(idx + (AED_FFT_SIZE / 4));
}

/* Перестановка за оберненим порядком бітів: для 512 точок — 9 бітів. */
static void bit_reverse(int16_t *re, int16_t *im)
{
    unsigned j = 0;
    for (unsigned i = 1; i < AED_FFT_SIZE; ++i) {
        unsigned bit = AED_FFT_SIZE >> 1;
        while (j & bit) {
            j ^= bit;
            bit >>= 1;
        }
        j |= bit;

        if (i < j) {
            int16_t tmp = re[i]; re[i] = re[j]; re[j] = tmp;
            tmp = im[i];         im[i] = im[j]; im[j] = tmp;
        }
    }
}

void fft_q15_512(int16_t *re, int16_t *im)
{
    bit_reverse(re, im);

    /* Класична DIT-схема: довжина метелика подвоюється щощабля. */
    for (unsigned len = 2; len <= AED_FFT_SIZE; len <<= 1) {
        const unsigned half = len >> 1;
        const unsigned step = AED_FFT_SIZE / len;

        for (unsigned base = 0; base < AED_FFT_SIZE; base += len) {
            unsigned tw = 0;
            for (unsigned k = 0; k < half; ++k, tw += step) {
                /* Обертальний множник e^(-j·2π·k/len). */
                const int32_t wr = cos_q15(tw);
                const int32_t wi = -(int32_t)sin_q15(tw);

                const unsigned a = base + k;
                const unsigned b = a + half;

                const int32_t tr = (wr * re[b] - wi * im[b]) >> 15;
                const int32_t ti = (wr * im[b] + wi * re[b]) >> 15;

                const int32_t ur = re[a];
                const int32_t ui = im[a];

                /* Поділ на 2 на кожному щаблі — див. коментар у заголовку. */
                re[a] = (int16_t)((ur + tr) >> 1);
                im[a] = (int16_t)((ui + ti) >> 1);
                re[b] = (int16_t)((ur - tr) >> 1);
                im[b] = (int16_t)((ui - ti) >> 1);
            }
        }
    }
}

uint32_t fft_q15_power(int16_t re, int16_t im)
{
    const int32_t r = re;
    const int32_t i = im;
    return (uint32_t)(r * r) + (uint32_t)(i * i);
}
