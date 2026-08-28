#include <stdint.h>
#include <stddef.h>
#include <string.h>

/* Допоміжне множення 64x64 з двома перенесеннями */
static inline uint64_t mac2(uint64_t a, uint64_t b, uint64_t c, uint64_t d, uint64_t *hi) {
    __uint128_t prod = (__uint128_t)a * b + c + d;
    *hi = (uint64_t)(prod >> 64);
    return (uint64_t)prod;
}

/* Сталочасове умовне віднімання без розгалужень */
static void sub_conditional_ct(uint64_t *u, const uint64_t *n, size_t k) {
    uint64_t borrow = 0;
    uint64_t diff[k];
    for (size_t i = 0; i < k; i++) {
        __uint128_t sub = (__uint128_t)u[i] - n[i] - borrow;
        diff[i] = (uint64_t)sub;
        borrow = (uint64_t)(sub >> 127) & 1;
    }
    uint64_t mask = (uint64_t)(-(int64_t)(1 - borrow));
    for (size_t i = 0; i < k; i++) {
        u[i] = (diff[i] & mask) | (u[i] & ~mask);
    }
}

/* Повне множення за Монтгомері методом CIOS */
void montgomery_mul_cios(const uint64_t *a, const uint64_t *b,
                         const uint64_t *n, size_t k,
                         uint64_t n0_prime, uint64_t *res) {
    uint64_t t[k + 2];
    memset(t, 0, sizeof(t));

    for (size_t i = 0; i < k; i++) {
        uint64_t carry = 0;
        for (size_t j = 0; j < k; j++) {
            t[j] = mac2(a[i], b[j], t[j], carry, &carry);
        }
        __uint128_t sum_carry = (__uint128_t)t[k] + carry;
        t[k] = (uint64_t)sum_carry;
        t[k + 1] = (uint64_t)(sum_carry >> 64);

        uint64_t m = (uint64_t)(t[0] * n0_prime);

        uint64_t c2 = 0;
        mac2(m, n[0], t[0], 0, &c2);

        for (size_t j = 1; j < k; j++) {
            t[j - 1] = mac2(m, n[j], t[j], c2, &c2);
        }

        __uint128_t sum2 = (__uint128_t)t[k] + c2;
        t[k - 1] = (uint64_t)sum2;
        t[k] = t[k + 1] + (uint64_t)(sum2 >> 64);
        t[k + 1] = 0;
    }

    memcpy(res, t, k * sizeof(uint64_t));
    sub_conditional_ct(res, n, k);
}
