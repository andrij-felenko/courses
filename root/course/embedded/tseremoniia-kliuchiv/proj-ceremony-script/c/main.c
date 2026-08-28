#include <stdint.h>
#include <stddef.h>
#include <string.h>
#include <stdbool.h>

#define GF256_POLY 0x11B

static uint8_t gf_exp[512];
static uint8_t gf_log[256];
static bool gf_initialized = false;

/* Ініціалізація таблиць логарифмів та експонент для GF(256) */
static void gf256_init(void) {
    if (gf_initialized) return;
    uint32_t val = 1;
    for (int i = 0; i < 255; i++) {
        gf_exp[i] = (uint8_t)val;
        gf_exp[i + 255] = (uint8_t)val;
        gf_log[val] = (uint8_t)i;
        val <<= 1;
        if (val & 0x100) {
            val ^= GF256_POLY;
        }
    }
    gf_log[0] = 0;
    gf_initialized = true;
}

/* Множення у полі GF(256) з захистом від нульових множників */
static inline uint8_t gf256_mul(uint8_t a, uint8_t b) {
    if (a == 0 || b == 0) return 0;
    return gf_exp[gf_log[a] + gf_log[b]];
}

/* Ділення a / b у полі GF(256) */
static inline uint8_t gf256_div(uint8_t a, uint8_t b) {
    if (a == 0) return 0;
    if (b == 0) return 0; /* Неприпустима операція в математиці */
    return gf_exp[(gf_log[a] + 255 - gf_log[b]) % 255];
}

/* Структура однієї частки секрету */
typedef struct {
    uint8_t x;                      /* Індекс частки (1..n) */
    uint8_t data[64];               /* Байти частки */
    size_t len;                     /* Довжина даних у байтах */
} shamir_share_t;

/* Безпечне затирання конфіденційної пам'яті */
static void secure_memzero(void *v, size_t n) {
    volatile uint8_t *p = (volatile uint8_t *)v;
    while (n--) *p++ = 0;
}

/*
 * Розщеплення секрету на n часток з порогом k.
 * random_bytes: буфер випадкових чисел розміром (k - 1) * len байтів.
 */
int shamir_split(const uint8_t *secret, size_t len,
                 uint8_t k, uint8_t n,
                 const uint8_t *random_bytes,
                 shamir_share_t *shares_out) {
    if (k < 2 || k > n || n > 255 || len > 64) return -1;
    gf256_init();

    for (uint8_t i = 0; i < n; i++) {
        shares_out[i].x = (uint8_t)(i + 1);
        shares_out[i].len = len;
        memset(shares_out[i].data, 0, sizeof(shares_out[i].data));
    }

    /* Побайтове обчислення полінома степеня k - 1 */
    for (size_t byte_idx = 0; byte_idx < len; byte_idx++) {
        uint8_t secret_byte = secret[byte_idx];
        
        for (uint8_t i = 0; i < n; i++) {
            uint8_t x = shares_out[i].x;
            uint8_t y = secret_byte; /* a_0 */
            uint8_t x_pow = x;

            for (uint8_t deg = 1; deg < k; deg++) {
                uint8_t coef = random_bytes[(deg - 1) * len + byte_idx];
                y ^= gf256_mul(coef, x_pow);
                x_pow = gf256_mul(x_pow, x);
            }
            shares_out[i].data[byte_idx] = y;
        }
    }
    return 0;
}

/*
 * Відновлення секрету з k наданих часток через інтерполяцію Лагранжа в точці x = 0.
 */
int shamir_combine(const shamir_share_t *shares_in, uint8_t k,
                   uint8_t *secret_out, size_t len) {
    if (k < 2 || len > 64) return -1;
    gf256_init();

    /* Перевірка унікальності точок x */
    for (uint8_t i = 0; i < k; i++) {
        if (shares_in[i].x == 0) return -2;
        for (uint8_t j = i + 1; j < k; j++) {
            if (shares_in[i].x == shares_in[j].x) return -2;
        }
    }

    /* Обчислення коефіцієнтів Лагранжа L_j(0) */
    uint8_t lagrange_weights[256];
    for (uint8_t j = 0; j < k; j++) {
        uint8_t num = 1;
        uint8_t den = 1;
        uint8_t xj = shares_in[j].x;

        for (uint8_t m = 0; m < k; m++) {
            if (m == j) continue;
            uint8_t xm = shares_in[m].x;
            num = gf256_mul(num, xm);            /* 0 - xm у полі характеристики 2 дорівнює xm */
            den = gf256_mul(den, xj ^ xm);       /* xj - xm у полі характеристики 2 дорівнює xj ^ xm */
        }
        lagrange_weights[j] = gf256_div(num, den);
    }

    /* Відновлення байтів секрету */
    for (size_t byte_idx = 0; byte_idx < len; byte_idx++) {
        uint8_t s = 0;
        for (uint8_t j = 0; j < k; j++) {
            s ^= gf256_mul(shares_in[j].data[byte_idx], lagrange_weights[j]);
        }
        secret_out[byte_idx] = s;
    }
    return 0;
}
