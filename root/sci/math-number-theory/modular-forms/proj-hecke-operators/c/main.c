#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>

/* Обчислення суми степеней дільників sigma_k(n) = sum_{d|n} d^k */
static uint64_t sum_divisor_powers(uint32_t n, uint32_t power) {
    uint64_t sum = 0;
    for (uint32_t d = 1; d * d <= n; ++d) {
        if (n % d == 0) {
            uint64_t p1 = 1;
            for (uint32_t i = 0; i < power; ++i) p1 *= d;
            sum += p1;

            uint32_t div2 = n / d;
            if (div2 != d) {
                uint64_t p2 = 1;
                for (uint32_t i = 0; i < power; ++i) p2 *= div2;
                sum += p2;
            }
        }
    }
    return sum;
}

/* Обчислення добутку двох степеневих рядів A(q) * B(q) mod q^(max_deg + 1) */
static void multiply_series(const int64_t *a, const int64_t *b, int64_t *res, size_t max_deg) {
    for (size_t n = 0; n <= max_deg; ++n) {
        res[n] = 0;
        for (size_t k = 0; k <= n; ++k) {
            res[n] += a[k] * b[n - k];
        }
    }
}

/* Дія оператора Гекке T_p на модулярну форму ваги weight */
static void apply_hecke_operator(const int64_t *a, int64_t *b, size_t max_deg, uint32_t p, uint32_t weight) {
    uint64_t p_pow = 1;
    for (uint32_t i = 0; i < weight - 1; ++i) p_pow *= p;

    for (size_t n = 0; n <= max_deg; ++n) {
        int64_t term1 = 0;
        if (n * p <= max_deg) {
            term1 = a[n * p];
        }
        int64_t term2 = 0;
        if (n % p == 0) {
            term2 = (int64_t)p_pow * a[n / p];
        }
        b[n] = term1 + term2;
    }
}

int main(void) {
    const size_t max_n = 10;
    int64_t *e4 = (int64_t *)calloc(max_n + 1, sizeof(int64_t));
    int64_t *e6 = (int64_t *)calloc(max_n + 1, sizeof(int64_t));
    int64_t *e4_2 = (int64_t *)calloc(max_n + 1, sizeof(int64_t));
    int64_t *e4_3 = (int64_t *)calloc(max_n + 1, sizeof(int64_t));
    int64_t *e6_2 = (int64_t *)calloc(max_n + 1, sizeof(int64_t));
    int64_t *delta = (int64_t *)calloc(max_n + 1, sizeof(int64_t));
    int64_t *t2_delta = (int64_t *)calloc(max_n + 1, sizeof(int64_t));

    if (!e4 || !e6 || !e4_2 || !e4_3 || !e6_2 || !delta || !t2_delta) {
        fprintf(stderr, "Помилка виділення пам'яті\n");
        free(e4); free(e6); free(e4_2); free(e4_3); free(e6_2); free(delta); free(t2_delta);
        return 1;
    }

    e4[0] = 1;
    e6[0] = 1;
    for (size_t n = 1; n <= max_n; ++n) {
        e4[n] = 240 * (int64_t)sum_divisor_powers((uint32_t)n, 3);
        e6[n] = -504 * (int64_t)sum_divisor_powers((uint32_t)n, 5);
    }

    multiply_series(e4, e4, e4_2, max_n);
    multiply_series(e4_2, e4, e4_3, max_n);
    multiply_series(e6, e6, e6_2, max_n);

    for (size_t n = 0; n <= max_n; ++n) {
        delta[n] = (e4_3[n] - e6_2[n]) / 1728;
    }

    printf("=== Коефіцієнти Фур'є E4, E6 та Delta (tau(n)) ===\n");
    printf("n\tE4(n)\t\tE6(n)\t\tDelta(n) [tau(n)]\n");
    for (size_t n = 1; n <= max_n; ++n) {
        printf("%zu\t%lld\t\t%lld\t\t%lld\n", n, (long long)e4[n], (long long)e6[n], (long long)delta[n]);
    }

    /* Дія оператора Гекке T_2 на параболічну форму Delta (вага 12) */
    apply_hecke_operator(delta, t2_delta, max_n, 2, 12);

    printf("\n=== Дія оператора Гекке T_2 на Delta (tau(2) = %lld) ===\n", (long long)delta[2]);
    printf("n\ttau(n)\t\tT_2(Delta)[n]\tВласне значення T_2(Delta) == tau(2)*tau(n)?\n");
    for (size_t n = 1; n <= 5; ++n) {
        int64_t expected = delta[2] * delta[n];
        printf("%zu\t%lld\t\t%lld\t\t%s (%lld)\n", 
               n, (long long)delta[n], (long long)t2_delta[n],
               (t2_delta[n] == expected) ? "ТАК" : "НІ", (long long)expected);
    }

    free(e4); free(e6); free(e4_2); free(e4_3); free(e6_2); free(delta); free(t2_delta);
    return 0;
}
