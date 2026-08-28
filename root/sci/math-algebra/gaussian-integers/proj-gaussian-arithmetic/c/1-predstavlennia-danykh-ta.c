#include <stdint.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <inttypes.h>

/* Структура гауссового цілого числа в C */
typedef struct {
    int64_t re;
    int64_t im;
} gauss_t;

/* Створення нового гауссового числа */
static inline gauss_t gauss_make(int64_t re, int64_t im) {
    gauss_t z = { re, im };
    return z;
}

/* Додавання: (a + bi) + (c + di) = (a + c) + (b + d)i */
static inline gauss_t gauss_add(gauss_t a, gauss_t b) {
    return gauss_make(a.re + b.re, a.im + b.im);
}

/* Віднімання: (a + bi) - (c + di) = (a - c) + (b - d)i */
static inline gauss_t gauss_sub(gauss_t a, gauss_t b) {
    return gauss_make(a.re - b.re, a.im - b.im);
}

/* Множення: (a + bi)·(c + di) = (ac - bd) + (ad + bc)i */
static inline gauss_t gauss_mul(gauss_t a, gauss_t b) {
    return gauss_make(
        a.re * b.re - a.im * b.im,
        a.re * b.im + a.im * b.re
    );
}

/* Комплексне спряження: a - bi */
static inline gauss_t gauss_conj(gauss_t a) {
    return gauss_make(a.re, -a.im);
}

/* Алгебраїчна норма: N(a + bi) = a^2 + b^2 */
static inline uint64_t gauss_norm(gauss_t a) {
    return (uint64_t)a.re * (uint64_t)a.re + (uint64_t)a.im * (uint64_t)a.im;
}

/* Перевірка на строгу рівність */
static inline bool gauss_eq(gauss_t a, gauss_t b) {
    return (a.re == b.re) && (a.im == b.im);
}

/* Перевірка на нуль */
static inline bool gauss_is_zero(gauss_t a) {
    return (a.re == 0) && (a.im == 0);
}

/* Перевірка, чи є число оборотною одиницею (1, i, -1, -i) */
static inline bool gauss_is_unit(gauss_t a) {
    return gauss_norm(a) == 1;
}
