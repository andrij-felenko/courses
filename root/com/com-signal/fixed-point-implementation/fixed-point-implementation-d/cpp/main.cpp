#include <stdint.h>

#define Q  15
#define RND (1LL << (Q - 1))          // 0.5 молодшого розряду — для округлення

// затиск 32-бітного значення у діапазон int16_t (насичення замість загортання)
static int16_t sat16(int32_t v) {
    if (v >  32767) return  32767;
    if (v < -32768) return -32768;
    return (int16_t)v;
}

// один вихідний відлік КІХ на 3 відводи; b[] і x[] — у Q15
int16_t fir3_q15(const int16_t b[3], const int16_t x[3]) {
    int64_t acc = 0;                  // широкий акумулятор: сума не переповниться
    for (int k = 0; k < 3; k++)
        acc += (int64_t)b[k] * x[k];  // Q15 × Q15 = Q30, копимо в Q30
    acc = (acc + RND) >> Q;           // округлюємо й вертаємо Q30 → Q15
    return sat16((int32_t)acc);       // звужуємо в 16 біт із насиченням
}
