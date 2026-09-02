#ifndef IIR_FIXED_H
#define IIR_FIXED_H

#include <stdbool.h>
#include <stdint.h>

/* Експоненційний фільтр низьких частот (IIR першого порядку)
   з коефіцієнтом alpha = 1/2^k: жодного множення, лише зсув.
   Стан тримається у форматі Q16.16, тому залишок ділення не гине
   і фільтр не застрягає в мертвій зоні. */

typedef struct {
    int32_t acc_q16; /* накопичувач у Q16.16 */
    uint8_t k;       /* alpha = 1 / 2^k */
    bool primed;     /* чи завантажено перший відлік */
} iir_q16_t;

void iir_q16_init(iir_q16_t *f, uint8_t k);
/* Вхід і вихід — цілі числа фізичних одиниць (наприклад, мм/с²). */
int32_t iir_q16_update(iir_q16_t *f, int32_t x);
int32_t iir_q16_value(const iir_q16_t *f);

/* Показова «наївна» реалізація: стан у цілих, залишок губиться. */
int16_t iir_naive_update(int16_t *state, int16_t x, uint8_t k);

#endif /* IIR_FIXED_H */
