/* Короткий FIR-фільтр згладжування струму фази.
 * Чотири відліки — саме той випадок, коли перевірка лічильника й перехід
 * на початок циклу коштують більше за самі множення.
 */
#ifndef FIR_H
#define FIR_H

#include <stdint.h>
#include "ramfunc.h"

#define FIR_TAPS 4U

typedef struct {
    float x[FIR_TAPS];   /* лінія затримки, x[0] — найсвіжіший відлік */
} fir_f32;

void fir_f32_reset(fir_f32 *f);

/* Розгорнутий фільтр у SRAM: жодного переходу, жодного штрафу Flash. */
RAM_FUNC float fir_f32_push(fir_f32 *f, float sample);

/* Той самий фільтр у форматі Q15 на парних інструкціях DSP.
   Повертає накопичувач Q30; вихід Q15 — через fir_q15_saturate(). */
int32_t fir_q15_dot4(const int16_t *x, const int16_t *h);

int16_t fir_q15_saturate(int32_t acc);

#endif /* FIR_H */
