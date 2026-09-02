#include "fir.h"

#include <string.h>
#include "stm32f4xx.h"

/* Вікно Ханна на чотири відліки, сума коефіцієнтів = 1. */
static const float k_taps[FIR_TAPS] = { 0.125f, 0.375f, 0.375f, 0.125f };

void fir_f32_reset(fir_f32 *f)
{
    memset(f->x, 0, sizeof f->x);
}

float fir_f32_push(fir_f32 *f, float sample)
{
    /* Зсув лінії затримки розгорнуто вручну: три VMOV замість циклу з переходом. */
    f->x[3] = f->x[2];
    f->x[2] = f->x[1];
    f->x[1] = f->x[0];
    f->x[0] = sample;

    float acc = 0.0f;

    /* Директива гарантує повне розгортання навіть на -O1: чотири VMLA.F32
       лінійно, без BNE наприкінці ітерації. */
#pragma GCC unroll 4
    for (unsigned i = 0U; i < FIR_TAPS; ++i) {
        acc += f->x[i] * k_taps[i];
    }
    return acc;
}

int32_t fir_q15_dot4(const int16_t *x, const int16_t *h)
{
#if defined(__ARM_FEATURE_DSP) && (__ARM_FEATURE_DSP == 1)
    uint32_t x01, x23, h01, h23;

    /* memcpy тут не копіює нічого: компілятор бачить чотири байти
       й ставить одну LDR. Заразом це єдиний законний спосіб прочитати
       пару int16 як uint32, не порушивши правил псевдонімів. */
    memcpy(&x01, &x[0], sizeof x01);
    memcpy(&x23, &x[2], sizeof x23);
    memcpy(&h01, &h[0], sizeof h01);
    memcpy(&h23, &h[2], sizeof h23);

    uint32_t acc = 0U;
    acc = __SMLAD(x01, h01, acc);   /* два множення 16x16 і два додавання за такт */
    acc = __SMLAD(x23, h23, acc);
    return (int32_t)acc;
#else
    int32_t acc = 0;
    for (unsigned i = 0U; i < 4U; ++i) {
        acc += (int32_t)x[i] * (int32_t)h[i];
    }
    return acc;
#endif
}

int16_t fir_q15_saturate(int32_t acc)
{
    /* __SSAT — одна інструкція замість пари порівнянь із переходами. */
    return (int16_t)__SSAT(acc >> 15, 16);
}
