#include <stdint.h>
#include <stdbool.h>
#include <stdio.h>

/* Незвідний многочлен Rijndael для AES: x^8 + x^4 + x^3 + x + 1 = 0x11B */
#define AES_POLY 0x11B

/* Додавання та віднімання в характеристиці 2 — це побітове XOR */
static inline uint8_t gf28_add(uint8_t a, uint8_t b) {
    return a ^ b;
}

/* Множення на x (xtime): зсув вліво на 1 біт з редукцією за модулем 0x11B */
static inline uint8_t gf28_xtime(uint8_t a) {
    return (uint8_t)((a << 1) ^ ((a & 0x80) ? 0x1B : 0x00));
}

/* Множення методом зсуву та додавання (Russian Peasant Multiplication) */
uint8_t gf28_mul(uint8_t a, uint8_t b) {
    uint8_t res = 0;
    while (b > 0) {
        if (b & 1) {
            res ^= a;
        }
        a = gf28_xtime(a);
        b >>= 1;
    }
    return res;
}

/* Автоморфізм Фробеніуса: σ(a) = a^2 */
static inline uint8_t gf28_frobenius(uint8_t a) {
    return gf28_mul(a, a);
}

/* Обчислення сліду: Tr(a) = a + a^2 + a^4 + a^8 + a^16 + a^32 + a^64 + a^128 */
uint8_t gf28_trace(uint8_t a) {
    uint8_t tr = a;
    uint8_t cur = a;
    for (int i = 1; i < 8; ++i) {
        cur = gf28_frobenius(cur);
        tr ^= cur;
    }
    return tr; /* результат завжди 0 або 1 */
}

/* Обчислення норми: N(a) = a · a^2 · a^4 · ... · a^128 = a^255 */
uint8_t gf28_norm(uint8_t a) {
    if (a == 0) return 0;
    /* У GF(2^8) для будь-якого ненульового елемента a^255 = 1 */
    return 1;
}

/* Обчислення степеня полінома (індекс старшого встановленого біта) */
static int poly_degree(uint32_t p) {
    int deg = -1;
    while (p > 0) {
        deg++;
        p >>= 1;
    }
    return deg;
}

/* Обернений елемент за розширеним алгоритмом Евкліда над F_2[x] */
uint8_t gf28_inv(uint8_t a) {
    if (a == 0) return 0; /* нуль не має оберненого */

    uint32_t r0 = AES_POLY, r1 = a;
    uint32_t v0 = 0, v1 = 1;

    while (r1 > 0) {
        int d0 = poly_degree(r0);
        int d1 = poly_degree(r1);
        int shift = d0 - d1;

        if (shift < 0) {
            /* Обмін залишків та коефіцієнтів Безу */
            uint32_t tmp_r = r0; r0 = r1; r1 = tmp_r;
            uint32_t tmp_v = v0; v0 = v1; v1 = tmp_v;
            shift = -shift;
        }

        r0 ^= (r1 << shift);
        v0 ^= (v1 << shift);
    }

    return (uint8_t)v0;
}

/* Таблиці експоненти та логарифма для швидкого множення через генератор g = 0x03 */
static uint8_t exp_table[256];
static uint8_t log_table[256];
static bool tables_initialized = false;

void gf28_init_tables(void) {
    if (tables_initialized) return;
    
    uint8_t val = 1;
    for (int i = 0; i < 255; ++i) {
        exp_table[i] = val;
        log_table[val] = (uint8_t)i;
        val = gf28_mul(val, 0x03); /* 0x03 (x + 1) — первісний елемент */
    }
    exp_table[255] = exp_table[0];
    log_table[0] = 0; /* логарифм нуля формально не визначений */
    tables_initialized = true;
}

/* Швидке табличне множення за O(1) */
uint8_t gf28_mul_fast(uint8_t a, uint8_t b) {
    if (a == 0 || b == 0) return 0;
    if (!tables_initialized) gf28_init_tables();
    int sum = log_table[a] + log_table[b];
    if (sum >= 255) sum -= 255;
    return exp_table[sum];
}

int main(void) {
    gf28_init_tables();

    uint8_t a = 0x57; /* x^6 + x^4 + x^2 + x + 1 */
    uint8_t b = 0x83; /* x^7 + x + 1 */

    uint8_t p_slow = gf28_mul(a, b);
    uint8_t p_fast = gf28_mul_fast(a, b);
    uint8_t a_inv = gf28_inv(a);
    uint8_t prod_inv = gf28_mul(a, a_inv);
    uint8_t tr_a = gf28_trace(a);

    printf("a = 0x%02X, b = 0x%02X\n", a, b);
    printf("a * b (xtime) = 0x%02X (очікується 0xC1)\n", p_slow);
    printf("a * b (таблиця)= 0x%02X\n", p_fast);
    printf("inv(a)        = 0x%02X\n", a_inv);
    printf("a * inv(a)    = 0x%02X (має бути 0x01)\n", prod_inv);
    printf("Tr(a)         = %u\n", tr_a);

    return 0;
}
