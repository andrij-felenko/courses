#include <stdint.h>
#include <stdbool.h>
#include <stdio.h>
#include <string.h>

#define RING_N 8
#define RING_Q 97

/* Структура полінома в круговому кільці Z_q[x] / (x^N + 1) */
typedef struct {
    int32_t coeffs[RING_N];
} CycloPoly;

/* Канонічне приведення за модулем q до діапазону [0, q - 1] */
static inline int32_t mod_q(int32_t val) {
    int32_t r = val % RING_Q;
    if (r < 0) {
        r += RING_Q;
    }
    return r;
}

/* Ініціалізація полінома нулями */
void poly_init_zero(CycloPoly *p) {
    for (size_t i = 0; i < RING_N; ++i) {
        p->coeffs[i] = 0;
    }
}

/* Додавання двох поліномів: out = (a + b) mod q */
void poly_add(CycloPoly *out, const CycloPoly *a, const CycloPoly *b) {
    for (size_t i = 0; i < RING_N; ++i) {
        out->coeffs[i] = mod_q(a->coeffs[i] + b->coeffs[i]);
    }
}

/* Віднімання двох поліномів: out = (a - b) mod q */
void poly_sub(CycloPoly *out, const CycloPoly *a, const CycloPoly *b) {
    for (size_t i = 0; i < RING_N; ++i) {
        out->coeffs[i] = mod_q(a->coeffs[i] - b->coeffs[i]);
    }
}

/* Множення полінома на скаляр: out = (a * scalar) mod q */
void poly_scalar_mul(CycloPoly *out, const CycloPoly *a, int32_t scalar) {
    int32_t s = mod_q(scalar);
    for (size_t i = 0; i < RING_N; ++i) {
        out->coeffs[i] = mod_q(a->coeffs[i] * s);
    }
}

/* Кругове множення за модулем Phi_{2N}(x) = x^N + 1: out = (a * b) mod (x^N + 1, q) */
void poly_mul_cyclotomic(CycloPoly *out, const CycloPoly *a, const CycloPoly *b) {
    int64_t prod[2 * RING_N];
    for (size_t i = 0; i < 2 * RING_N; ++i) {
        prod[i] = 0;
    }

    /* 1. Звичайне множення поліномів (згортка) */
    for (size_t i = 0; i < RING_N; ++i) {
        for (size_t j = 0; j < RING_N; ++j) {
            prod[i + j] += (int64_t)a->coeffs[i] * (int64_t)b->coeffs[j];
        }
    }

    /* 2. Негациклічна редукція x^N = -1 та приведення mod q */
    for (size_t i = 0; i < RING_N; ++i) {
        int64_t low = prod[i];
        int64_t high = prod[i + RING_N];
        int32_t reduced = (int32_t)((low - high) % RING_Q);
        out->coeffs[i] = mod_q(reduced);
    }
}

/* Друк полінома */
void poly_print(const char *label, const CycloPoly *p) {
    printf("%s: [", label);
    for (size_t i = 0; i < RING_N; ++i) {
        printf("%d%s", p->coeffs[i], (i + 1 < RING_N) ? ", " : "");
    }
    printf("]\n");
}

int main(void) {
    CycloPoly a, b, sum, prod;
    poly_init_zero(&a);
    poly_init_zero(&b);

    /* a(x) = 3 + 2x + x^7 */
    a.coeffs[0] = 3;
    a.coeffs[1] = 2;
    a.coeffs[7] = 1;

    /* b(x) = 5 + 4x^2 + 2x^7 */
    b.coeffs[0] = 5;
    b.coeffs[2] = 4;
    b.coeffs[7] = 2;

    poly_add(&sum, &a, &b);
    poly_mul_cyclotomic(&prod, &a, &b);

    printf("=== Арифметика в круговому кільці Z_%d[x] / (x^%d + 1) ===\n", RING_Q, RING_N);
    poly_print("a(x)", &a);
    poly_print("b(x)", &b);
    poly_print("a(x) + b(x)", &sum);
    poly_print("a(x) * b(x) mod (x^8 + 1)", &prod);

    return 0;
}
