#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
#include <stdlib.h>

/* Просте число Мерсенна p = 2^61 - 1 */
#define P61 ((1ULL << 61) - 1)

typedef struct {
    uint64_t a;
    uint64_t b;
    uint64_t m;
} modular_hasher_t;

typedef struct {
    uint64_t a;     /* Повинно бути непарним */
    uint32_t shift; /* 64 - M */
    uint64_t mask;  /* m - 1 */
} multiply_shift_hasher_t;

/* Швидке множення за модулем 2^61 - 1 */
static inline uint64_t mod61(unsigned __int128 val) {
    uint64_t sum = (uint64_t)(val & P61) + (uint64_t)(val >> 61);
    return (sum >= P61) ? (sum - P61) : sum;
}

void modular_hasher_init(modular_hasher_t *h, uint64_t m, uint64_t seed_a, uint64_t seed_b) {
    h->m = m;
    h->a = (seed_a % (P61 - 1)) + 1; /* a ∈ [1 .. P61-1] */
    h->b = seed_b % P61;
}

uint64_t modular_hasher_eval(const modular_hasher_t *h, uint64_t x) {
    unsigned __int128 prod = (unsigned __int128)h->a * x + h->b;
    uint64_t rem = mod61(prod);
    return rem % h->m;
}

void multiply_shift_init(multiply_shift_hasher_t *h, uint32_t M, uint64_t seed_a) {
    h->shift = 64 - M;
    h->mask = (1ULL << M) - 1;
    h->a = seed_a | 1ULL; /* Гарантуємо непарність */
}

uint64_t multiply_shift_eval(const multiply_shift_hasher_t *h, uint64_t x) {
    return (h->a * x) >> h->shift;
}
