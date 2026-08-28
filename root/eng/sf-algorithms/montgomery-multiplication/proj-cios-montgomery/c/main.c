#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
#include <string.h>

/* Обчислення n0' = (-N[0]^(-1)) mod 2^64 за 6 кроків ітерації Гензеля */
uint64_t montgomery_compute_n0_prime(uint64_t n0) {
    uint64_t inv = 1;
    for (int i = 0; i < 6; i++) {
        inv = inv * (2 - n0 * inv);
    }
    return (uint64_t)(-(int64_t)inv);
}

/* Допоміжне множення з накопиченням 64x64 -> 128 бітів з двома доданками перенесення */
static inline uint64_t mac2(uint64_t a, uint64_t b, uint64_t c, uint64_t d, uint64_t *hi) {
    __uint128_t prod = (__uint128_t)a * b + c + d;
    *hi = (uint64_t)(prod >> 64);
    return (uint64_t)prod;
}

/* Сталочасове умовне віднімання: якщо u >= n, то u = u - n (без розгалужень) */
static void montgomery_sub_conditional(uint64_t *u, const uint64_t *n, size_t k) {
    uint64_t borrow = 0;
    /* Тимчасовий буфер для результату віднімання */
    uint64_t diff[k];
    
    for (size_t i = 0; i < k; i++) {
        __uint128_t sub = (__uint128_t)u[i] - n[i] - borrow;
        diff[i] = (uint64_t)sub;
        borrow = (uint64_t)(sub >> 127) & 1; /* Ознака позички */
    }

    /* Маска вибору: якщо borrow == 0 (тобто u >= n), mask = 0xFF..FF; інакше 0x00..00 */
    uint64_t mask = (uint64_t)(-(int64_t)(1 - borrow));
    for (size_t i = 0; i < k; i++) {
        u[i] = (diff[i] & mask) | (u[i] & ~mask);
    }
}

/* Алгоритм CIOS (Coarsely Integrated Operand Scanning) */
void montgomery_mul_cios(const uint64_t *a, const uint64_t *b,
                         const uint64_t *n, size_t k,
                         uint64_t n0_prime, uint64_t *res) {
    /* Робочий акумулятор розміром k + 2 слів */
    uint64_t t[k + 2];
    memset(t, 0, sizeof(t));

    for (size_t i = 0; i < k; i++) {
        /* 1. Множення й накопичення рядка: T = T + a[i] * B */
        uint64_t carry = 0;
        for (size_t j = 0; j < k; j++) {
            t[j] = mac2(a[i], b[j], t[j], carry, &carry);
        }
        __uint128_t sum_carry = (__uint128_t)t[k] + carry;
        t[k] = (uint64_t)sum_carry;
        t[k + 1] = (uint64_t)(sum_carry >> 64);

        /* 2. Обчислення коефіцієнта редукції для молодшого лімба */
        uint64_t m = (uint64_t)(t[0] * n0_prime);

        /* 3. Додавання m * N та зсув праворуч на 1 слово */
        uint64_t c2 = 0;
        mac2(m, n[0], t[0], 0, &c2); /* Молодший лімб стає нулем і ігнорується */

        for (size_t j = 1; j < k; j++) {
            t[j - 1] = mac2(m, n[j], t[j], c2, &c2);
        }

        __uint128_t sum2 = (__uint128_t)t[k] + c2;
        t[k - 1] = (uint64_t)sum2;
        t[k] = t[k + 1] + (uint64_t)(sum2 >> 64);
        t[k + 1] = 0;
    }

    /* Копіювання результату в вихідний масив */
    memcpy(res, t, k * sizeof(uint64_t));

    /* Фінальна корекція U < 2N -> U < N */
    montgomery_sub_conditional(res, n, k);
}

/* Алгоритм SOS (Separated Operand Scanning) */
void montgomery_mul_sos(const uint64_t *a, const uint64_t *b,
                        const uint64_t *n, size_t k,
                        uint64_t n0_prime, uint64_t *res) {
    /* Буфер подвійної довжини 2k + 1 слів */
    uint64_t t[2 * k + 1];
    memset(t, 0, sizeof(t));

    /* Фаза 1: Повне множення шкільним методом T = A * B */
    for (size_t i = 0; i < k; i++) {
        uint64_t carry = 0;
        for (size_t j = 0; j < k; j++) {
            t[i + j] = mac2(a[i], b[j], t[i + j], carry, &carry);
        }
        t[i + k] = carry;
    }

    /* Фаза 2: Редукція Монтгомері */
    for (size_t i = 0; i < k; i++) {
        uint64_t m = (uint64_t)(t[i] * n0_prime);
        uint64_t carry = 0;
        for (size_t j = 0; j < k; j++) {
            t[i + j] = mac2(m, n[j], t[i + j], carry, &carry);
        }
        /* Просування перенесення */
        size_t idx = i + k;
        while (carry && idx < 2 * k + 1) {
            __uint128_t sum = (__uint128_t)t[idx] + carry;
            t[idx] = (uint64_t)sum;
            carry = (uint64_t)(sum >> 64);
            idx++;
        }
    }

    /* Зсув на k слів (вибірка t[k .. 2k-1]) */
    memcpy(res, &t[k], k * sizeof(uint64_t));

    /* Фінальна корекція */
    montgomery_sub_conditional(res, n, k);
}
