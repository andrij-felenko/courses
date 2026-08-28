#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <stdbool.h>

/* --- 1. Алгоритм Бйорка — Перейри для дійсних чисел (double) --- */

/*
 * Розв'язує систему V_n * c = y за час O(n^2) та з пам'яттю O(n).
 * Вхідні параметри:
 *   n - розмірність системи
 *   x - масив попарно різних вузлів розміру n
 *   y - масив вхідних значень правої частини розміру n
 *   c_out - масив для запису знайдених коефіцієнтів розміру n
 * Повертає true у разі успіху, false якщо виявлено однакові вузли.
 */
bool bjorck_pereyra_solve_real(size_t n, const double *x, const double *y, double *c_out) {
    if (!x || !y || !c_out || n == 0) {
        return false;
    }

    /* Перевірка на збіг вузлів для уникнення ділення на нуль */
    for (size_t i = 0; i < n; ++i) {
        for (size_t j = i + 1; j < n; ++j) {
            if (x[i] == x[j]) {
                return false;
            }
        }
    }

    /* Копіюємо праву частину в робочий масив для обчислень in-place */
    memcpy(c_out, y, n * sizeof(double));

    /* Етап 1: Обчислення коефіцієнтів Ньютона (розділені різниці) */
    for (size_t k = 0; k < n - 1; ++k) {
        for (size_t i = n - 1; i > k; --i) {
            double denominator = x[i] - x[i - k - 1];
            c_out[i] = (c_out[i] - c_out[i - 1]) / denominator;
        }
    }

    /* Етап 2: Перетворення базису Ньютона у стандартні мономи */
    for (size_t k = n - 1; k > 0; --k) {
        size_t node_idx = k - 1;
        for (size_t i = node_idx; i < n - 1; ++i) {
            c_out[i] = c_out[i] - c_out[i + 1] * x[node_idx];
        }
    }

    return true;
}

/* --- 2. Арифметика скінченного поля GF(256) для схеми Шаміра --- */

static uint8_t gf_exp[512];
static uint8_t gf_log[256];
static bool gf_initialized = false;

static void gf256_init(void) {
    if (gf_initialized) return;
    uint32_t val = 1;
    for (int i = 0; i < 255; ++i) {
        gf_exp[i] = (uint8_t)val;
        gf_exp[i + 255] = (uint8_t)val;
        gf_log[val] = (uint8_t)i;
        val <<= 1;
        if (val & 0x100) {
            val ^= 0x11B; /* Поліном x^8 + x^4 + x^3 + x + 1 */
        }
    }
    gf_log[0] = 0; /* Умовне значення для log(0) */
    gf_initialized = true;
}

static inline uint8_t gf256_add(uint8_t a, uint8_t b) {
    return a ^ b;
}

static inline uint8_t gf256_mul(uint8_t a, uint8_t b) {
    if (a == 0 || b == 0) return 0;
    return gf_exp[gf_log[a] + gf_log[b]];
}

static inline uint8_t gf256_div(uint8_t a, uint8_t b) {
    if (b == 0) return 0; /* Помилка ділення на 0 */
    if (a == 0) return 0;
    return gf_exp[(gf_log[a] + 255 - gf_log[b]) % 255];
}

/* Структура частки секрету */
typedef struct {
    uint8_t x; /* Ідентифікатор учасника (x_i != 0) */
    uint8_t y; /* Значення полінома P(x_i) */
} ShamirShare;

/*
 * Розділення байта секрету на n часток із порогом k.
 */
bool shamir_split_byte(uint8_t secret, size_t n, size_t k, ShamirShare *shares_out) {
    if (k > n || k == 0 || n >= 256 || !shares_out) return false;
    gf256_init();

    uint8_t *coeffs = (uint8_t *)malloc(k);
    if (!coeffs) return false;

    coeffs[0] = secret;
    for (size_t i = 1; i < k; ++i) {
        coeffs[i] = (uint8_t)(rand() % 255 + 1);
    }

    for (size_t i = 0; i < n; ++i) {
        uint8_t x_val = (uint8_t)(i + 1);
        uint8_t y_val = coeffs[k - 1];
        /* Схема Горнера над GF(256) */
        for (int j = (int)k - 2; j >= 0; --j) {
            y_val = gf256_add(gf256_mul(y_val, x_val), coeffs[j]);
        }
        shares_out[i].x = x_val;
        shares_out[i].y = y_val;
    }

    free(coeffs);
    return true;
}

/*
 * Відновлення секрету за k частками за схемою Вандермонда/Лагранжа.
 */
uint8_t shamir_recover_byte(size_t k, const ShamirShare *shares) {
    if (!shares || k == 0) return 0;
    gf256_init();

    uint8_t secret = 0;
    for (size_t i = 0; i < k; ++i) {
        uint8_t num = 1;
        uint8_t den = 1;
        for (size_t j = 0; j < k; ++j) {
            if (i == j) continue;
            num = gf256_mul(num, shares[j].x);
            den = gf256_mul(den, gf256_add(shares[j].x, shares[i].x));
        }
        uint8_t lagrange_weight = gf256_div(num, den);
        uint8_t term = gf256_mul(shares[i].y, lagrange_weight);
        secret = gf256_add(secret, term);
    }
    return secret;
}

int main(void) {
    printf("=== 1. Тест алгоритму Бйорка — Перейри (double) ===\n");
    const size_t n = 4;
    double x_nodes[4] = {1.0, 2.0, 4.0, 5.0};
    double y_vals[4]  = {2.0, 5.0, 17.0, 26.0}; /* P(x) = x^2 + 1: c = [1, 0, 1, 0] */
    double c_res[4];

    if (bjorck_pereyra_solve_real(n, x_nodes, y_vals, c_res)) {
        printf("Знайдені коефіцієнти мономів c_j:\n");
        for (size_t i = 0; i < n; ++i) {
            printf("  c[%zu] = %6.2f (очікувалось: %6.2f)\n",
                   i, c_res[i], (i == 0 ? 1.0 : (i == 2 ? 1.0 : 0.0)));
        }
    }

    printf("\n=== 2. Тест розділення секрету Шаміра (GF(256)) ===\n");
    uint8_t secret = 0xA5; /* Початковий секрет: 165 */
    size_t total_n = 5;
    size_t threshold_k = 3;
    ShamirShare shares[5];

    shamir_split_byte(secret, total_n, threshold_k, shares);
    printf("Згенеровано %zu часток для секрету 0x%02X (поріг %zu):\n",
           total_n, secret, threshold_k);
    for (size_t i = 0; i < total_n; ++i) {
        printf("  Частка %zu: x = %u, y = 0x%02X\n", i + 1, shares[i].x, shares[i].y);
    }

    /* Відновлення за частками 0, 2, 4 */
    ShamirShare subset[3] = {shares[0], shares[2], shares[4]};
    uint8_t recovered = shamir_recover_byte(threshold_k, subset);
    printf("Відновлений секрет за 3 довільними частками: 0x%02X (%s)\n",
           recovered, (recovered == secret ? "УСПІХ" : "ПОМИЛКА"));

    return 0;
}
