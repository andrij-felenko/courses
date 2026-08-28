#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

#define GF_POLY 0x11B
#define FIELD_SIZE 256

static uint8_t gf_exp[512];
static uint8_t gf_log[FIELD_SIZE];
static int gf_initialized = 0;

/* Ініціалізація таблиць поля Галуа GF(256) з генератором alpha = 3 */
static void gf_init(void) {
    if (gf_initialized) return;
    uint8_t x = 1;
    for (int i = 0; i < 255; i++) {
        gf_exp[i] = x;
        gf_log[x] = (uint8_t)i;
        /* Множення x на alpha (3 = 2 XOR 1) */
        uint16_t x2 = (uint16_t)(x << 1);
        if (x2 & 0x100) x2 ^= GF_POLY;
        x ^= (uint8_t)x2;
    }
    for (int i = 255; i < 512; i++) {
        gf_exp[i] = gf_exp[i - 255];
    }
    gf_log[0] = 0; /* Невизначено, обробляється окремо */
    gf_initialized = 1;
}

static uint8_t gf_mul(uint8_t a, uint8_t b) {
    if (a == 0 || b == 0) return 0;
    return gf_exp[gf_log[a] + gf_log[b]];
}

static uint8_t gf_div(uint8_t a, uint8_t b) {
    if (b == 0) return 0; /* Помилка: ділення на нуль */
    if (a == 0) return 0;
    return gf_exp[gf_log[a] - gf_log[b] + 255];
}

typedef struct {
    uint8_t x;       /* Ідентифікатор учасника (x != 0) */
    uint8_t *data;   /* Масив значень y для кожного байта секрету */
    size_t len;      /* Довжина секрету в байтах */
} ShareC;

/* Генерація n часток для секрету довжиною secret_len байт з порогом k */
ShareC* create_shares_c(const uint8_t *secret, size_t secret_len, int k, int n) {
    gf_init();
    if (k < 1 || k > n || n >= FIELD_SIZE || secret == NULL) return NULL;

    ShareC *shares = (ShareC*)malloc(sizeof(ShareC) * n);
    if (!shares) return NULL;

    for (int i = 0; i < n; i++) {
        shares[i].x = (uint8_t)(i + 1);
        shares[i].len = secret_len;
        shares[i].data = (uint8_t*)malloc(secret_len);
    }

    uint8_t *coeffs = (uint8_t*)malloc(k);

    for (size_t byte_idx = 0; byte_idx < secret_len; byte_idx++) {
        coeffs[0] = secret[byte_idx]; /* Секрет це вільний член f(0) */
        for (int c = 1; c < k; c++) {
            coeffs[c] = (uint8_t)(rand() % 256); /* У реальності: CSPRNG */
        }

        for (int i = 0; i < n; i++) {
            uint8_t x_val = shares[i].x;
            uint8_t y_val = coeffs[0];
            uint8_t x_pow = 1;

            for (int c = 1; c < k; c++) {
                x_pow = gf_mul(x_pow, x_val);
                y_val ^= gf_mul(coeffs[c], x_pow);
            }
            shares[i].data[byte_idx] = y_val;
        }
    }

    free(coeffs);
    return shares;
}

/* Відновлення секрету за k частками через інтерполяцію Лагранжа */
uint8_t* reconstruct_secret_c(const ShareC *shares, int k, size_t *out_len) {
    gf_init();
    if (shares == NULL || k < 1) return NULL;

    size_t secret_len = shares[0].len;
    uint8_t *secret = (uint8_t*)calloc(secret_len, sizeof(uint8_t));
    if (!secret) return NULL;

    for (size_t byte_idx = 0; byte_idx < secret_len; byte_idx++) {
        uint8_t reconstructed_byte = 0;

        for (int i = 0; i < k; i++) {
            uint8_t xi = shares[i].x;
            uint8_t yi = shares[i].data[byte_idx];

            /* Обчислення базисного полінома Лагранжа li(0) */
            uint8_t li_0 = 1;
            for (int j = 0; j < k; j++) {
                if (i == j) continue;
                uint8_t xj = shares[j].x;
                /* li(0) *= xj / (xj ^ xi) */
                uint8_t num = xj;
                uint8_t den = xj ^ xi;
                li_0 = gf_mul(li_0, gf_div(num, den));
            }
            reconstructed_byte ^= gf_mul(yi, li_0);
        }
        secret[byte_idx] = reconstructed_byte;
    }

    *out_len = secret_len;
    return secret;
}

void free_shares_c(ShareC *shares, int n) {
    if (!shares) return;
    for (int i = 0; i < n; i++) {
        free(shares[i].data);
    }
    free(shares);
}
