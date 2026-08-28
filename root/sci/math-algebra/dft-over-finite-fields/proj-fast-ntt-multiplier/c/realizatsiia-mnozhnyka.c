#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

/* Параметри поля: просте число Ферма p = 65537 = 2^16 + 1 */
#define MODULUS 65537ULL
#define MONT_R  (1ULL << 32)
#define MONT_R_MASK 0xFFFFFFFFULL

/* Попередньо обчислені константи Монтгомері:
   MONT_R2 = R^2 mod p = (2^32)^2 mod 65537 = 1ULL
   P_INV   = -p^(-1) mod 2^32 = 4294901759ULL */
#define MONT_R2 1ULL
#define P_INV   4294901759ULL

/* Редукція Монтгомері REDC: обчислює (T * R^(-1)) mod p */
static inline uint32_t mont_reduce(uint64_t T) {
    uint64_t m = (uint32_t)((uint32_t)T * (uint32_t)P_INV);
    uint64_t t = (T + m * MODULUS) >> 32;
    if (t >= MODULUS) {
        t -= MODULUS;
    }
    return (uint32_t)t;
}

/* Переведення числа у форму Монтгомері: x * R mod p */
static inline uint32_t to_mont(uint32_t x) {
    return mont_reduce((uint64_t)x * MONT_R2);
}

/* Переведення з форми Монтгомері у звичайну форму */
static inline uint32_t from_mont(uint32_t x_mont) {
    return mont_reduce((uint64_t)x_mont);
}

/* Множення Монтгомері: (a * b * R) mod p */
static inline uint32_t mont_mul(uint32_t a_mont, uint32_t b_mont) {
    return mont_reduce((uint64_t)a_mont * (uint64_t)b_mont);
}

/* Швидке піднесення до степеня у скінченному полі */
static uint32_t power_mod(uint32_t base, uint32_t exp, uint32_t mod) {
    uint64_t res = 1;
    uint64_t b = base % mod;
    while (exp > 0) {
        if (exp & 1) res = (res * b) % mod;
        b = (b * b) % mod;
        exp >>= 1;
    }
    return (uint32_t)res;
}

/* Знаходження первісного кореня степеня n у полі */
static uint32_t get_root_of_unity(uint32_t n) {
    /* Генератор GF(65537)* дорівнює g = 3 */
    uint32_t g = 3;
    uint32_t exp = (MODULUS - 1) / n;
    return power_mod(g, exp, MODULUS);
}

/* Прямий NTT за алгоритмом Джентльмена — Сенде (DIF)
   Вхід: природний порядок. Вихід: інверсно-бітовий порядок. */
void ntt_dif(uint32_t *a, uint32_t n, const uint32_t *twiddles_mont) {
    uint32_t t = n >> 1;
    uint32_t tw_idx = 1;
    while (t > 0) {
        for (uint32_t i = 0; i < n; i += (t << 1)) {
            uint32_t w = twiddles_mont[tw_idx++];
            for (uint32_t j = i; j < i + t; j++) {
                uint32_t u = a[j];
                uint32_t v = a[j + t];
                /* u + v mod p */
                a[j] = (u + v >= MODULUS) ? (u + v - MODULUS) : (u + v);
                /* (u - v) * w mod p */
                uint32_t diff = (u >= v) ? (u - v) : (u + MODULUS - v);
                a[j + t] = mont_mul(diff, w);
            }
        }
        t >>= 1;
    }
}

/* Обернений INTT за алгоритмом Кулі — Тьюкі (DIT)
   Вхід: інверсно-бітовий порядок. Вихід: природний порядок. */
void intt_dit(uint32_t *a, uint32_t n, const uint32_t *inv_twiddles_mont) {
    uint32_t t = 1;
    uint32_t tw_idx = 1;
    while (t < n) {
        for (uint32_t i = 0; i < n; i += (t << 1)) {
            uint32_t w = inv_twiddles_mont[tw_idx++];
            for (uint32_t j = i; j < i + t; j++) {
                uint32_t u = a[j];
                uint32_t v = mont_mul(a[j + t], w);
                /* u + v * w mod p */
                a[j] = (u + v >= MODULUS) ? (u + v - MODULUS) : (u + v);
                /* u - v * w mod p */
                a[j + t] = (u >= v) ? (u - v) : (u + MODULUS - v);
            }
        }
        t <<= 1;
    }
    /* Масштабування на 1/n mod p */
    uint32_t n_inv = power_mod(n, MODULUS - 2, MODULUS);
    uint32_t n_inv_mont = to_mont(n_inv);
    for (uint32_t i = 0; i < n; i++) {
        a[i] = mont_mul(a[i], n_inv_mont);
    }
}

/* Таблиця поворотних коефіцієнтів у порядку бітового проріджування */
void precompute_twiddles(uint32_t n, uint32_t *tw, uint32_t *inv_tw) {
    uint32_t root = get_root_of_unity(n);
    uint32_t inv_root = power_mod(root, MODULUS - 2, MODULUS);

    uint32_t root_mont = to_mont(root);
    uint32_t inv_root_mont = to_mont(inv_root);

    uint32_t idx = 1;
    for (uint32_t len = n >> 1; len > 0; len >>= 1) {
        uint32_t cur = to_mont(1);
        uint32_t cur_inv = to_mont(1);
        uint32_t step = power_mod(root, (MODULUS - 1) / (n / len), MODULUS);
        uint32_t step_inv = power_mod(inv_root, (MODULUS - 1) / (n / len), MODULUS);
        uint32_t step_m = to_mont(step);
        uint32_t step_inv_m = to_mont(step_inv);

        for (uint32_t j = 0; j < (n / (len << 1)); j++) {
            tw[idx] = cur;
            inv_tw[idx] = cur_inv;
            idx++;
            cur = mont_mul(cur, step_m);
            cur_inv = mont_mul(cur_inv, step_inv_m);
        }
    }
}

/* Множення двох многочленів через конвеєр NTT */
void poly_multiply_ntt(const uint32_t *poly_a, size_t deg_a,
                       const uint32_t *poly_b, size_t deg_b,
                       uint32_t *res, size_t *res_deg) {
    size_t min_n = deg_a + deg_b + 1;
    uint32_t n = 1;
    while (n < min_n) n <<= 1;

    uint32_t *a = (uint32_t *)calloc(n, sizeof(uint32_t));
    uint32_t *b = (uint32_t *)calloc(n, sizeof(uint32_t));
    uint32_t *tw = (uint32_t *)calloc(n, sizeof(uint32_t));
    uint32_t *inv_tw = (uint32_t *)calloc(n, sizeof(uint32_t));

    precompute_twiddles(n, tw, inv_tw);

    /* Копіювання та переведення в простір Монтгомері */
    for (size_t i = 0; i <= deg_a; i++) a[i] = to_mont(poly_a[i]);
    for (size_t i = 0; i <= deg_b; i++) b[i] = to_mont(poly_b[i]);

    /* Прямий NTT (DIF) */
    ntt_dif(a, n, tw);
    ntt_dif(b, n, tw);

    /* Поточкове множення в спектральній області */
    for (uint32_t i = 0; i < n; i++) {
        a[i] = mont_mul(a[i], b[i]);
    }

    /* Обернений NTT (DIT) */
    intt_dit(a, n, inv_tw);

    /* Повернення результату зі зняттям представлення Монтгомері */
    *res_deg = deg_a + deg_b;
    for (size_t i = 0; i <= *res_deg; i++) {
        res[i] = from_mont(a[i]);
    }

    free(a);
    free(b);
    free(tw);
    free(inv_tw);
}
