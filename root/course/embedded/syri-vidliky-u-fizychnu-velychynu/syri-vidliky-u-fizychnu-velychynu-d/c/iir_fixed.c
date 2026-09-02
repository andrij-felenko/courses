#include "iir_fixed.h"

#include "fixedq16.h"

/* Стан Q16.16 має 15 бітів цілої частини — вхід мусить у них уміститися. */
#define IIR_INPUT_BITS 16u
#define IIR_MAX_SHIFT 15u

void iir_q16_init(iir_q16_t *f, uint8_t k) {
    f->acc_q16 = 0;
    f->k = (k > IIR_MAX_SHIFT) ? (uint8_t)IIR_MAX_SHIFT : k;
    f->primed = false;
}

int32_t iir_q16_update(iir_q16_t *f, int32_t x) {
    const int32_t xs = sat_bits(x, IIR_INPUT_BITS);
    const int32_t x_q16 = xs * Q16_ONE; /* xs у межах int16 — переповнення немає */

    if (!f->primed) {
        /* Перший відлік завантажуємо напряму: інакше фільтр повзе до
           справжнього значення десятки періодів після ввімкнення. */
        f->acc_q16 = x_q16;
        f->primed = true;
        return xs;
    }

    {
        /* Різниця двох крайніх значень Q16.16 не влазить в int32 —
           саме тут наївний код тихо переповнюється. */
        const int64_t diff = (int64_t)x_q16 - (int64_t)f->acc_q16;
        f->acc_q16 = sat_from_i64((int64_t)f->acc_q16 + (diff >> f->k));
    }
    return q16_to_int(f->acc_q16);
}

int32_t iir_q16_value(const iir_q16_t *f) {
    return q16_to_int(f->acc_q16);
}

int16_t iir_naive_update(int16_t *state, int16_t x, uint8_t k) {
    /* Мертва зона: щойно |x - state| падає нижче 2^k, зсув обнуляє
       приріст і фільтр застрягає, не дійшовши до справжнього середнього. */
    const int32_t s = (int32_t)*state;
    *state = sat_to_i16(s + (((int32_t)x - s) >> k));
    return *state;
}
