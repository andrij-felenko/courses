#include <stdint.h>

/* Стан цілочисельного експоненційного фільтра низьких частот */
typedef struct {
    int32_t state_q16; /* Внутрішній стан у форматі Q16.16 */
    uint8_t shift_k;   /* Коефіцієнт згладжування: alpha = 1 / 2^k */
} iir_fixed_filter_t;

void iir_fixed_init(iir_fixed_filter_t *f, uint8_t k, int16_t initial_val) {
    f->shift_k = k;
    f->state_q16 = (int32_t)initial_val << 16;
}

int16_t iir_fixed_update(iir_fixed_filter_t *f, int16_t input) {
    int32_t input_q16 = (int32_t)input << 16;
    /* Оновлення стану без втрати залишку: state += (input - state) >> k */
    f->state_q16 += (input_q16 - f->state_q16) >> f->shift_k;
    /* Повернення результату з симетричним округленням */
    return (int16_t)((f->state_q16 + (1 << 15)) >> 16);
}
