#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <math.h>

/* Обчислення суми степенів дільників: sigma_k(n) = sum_{d | n} d^k */
static uint64_t sum_divisor_powers(uint32_t n, uint32_t power) {
    uint64_t sum = 0;
    for (uint32_t d = 1; d * d <= n; ++d) {
        if (n % d == 0) {
            uint64_t p1 = 1;
            for (uint32_t i = 0; i < power; ++i) {
                p1 *= d;
            }
            sum += p1;

            uint32_t div2 = n / d;
            if (div2 != d) {
                uint64_t p2 = 1;
                for (uint32_t i = 0; i < power; ++i) {
                    p2 *= div2;
                }
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
    for (uint32_t i = 0; i < weight - 1; ++i) {
        p_pow *= p;
    }

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

/* Перевірка тотожності двох рядів до степеня max_deg */
static bool compare_series(const int64_t *a, const int64_t *b, size_t max_deg) {
    for (size_t n = 0; n <= max_deg; ++n) {
        if (a[n] != b[n]) {
            return false;
        }
    }
    return true;
}

/* Друк коефіцієнтів ряду */
static void print_series_table(const char *title, const int64_t *coeffs, size_t max_deg) {
    printf("%s:\n", title);
    printf("  n:      ");
    for (size_t n = 0; n <= max_deg && n <= 6; ++n) {
        printf("%8zu ", n);
    }
    printf("\n  coeffs: ");
    for (size_t n = 0; n <= max_deg && n <= 6; ++n) {
        printf("%8lld ", (long long)coeffs[n]);
    }
    printf("\n\n");
}

int main(void) {
    const size_t max_n = 10;
    int64_t *e4 = (int64_t *)calloc(max_n + 1, sizeof(int64_t));
    int64_t *e6 = (int64_t *)calloc(max_n + 1, sizeof(int64_t));
    int64_t *e8 = (int64_t *)calloc(max_n + 1, sizeof(int64_t));
    int64_t *e10 = (int64_t *)calloc(max_n + 1, sizeof(int64_t));
    int64_t *e14 = (int64_t *)calloc(max_n + 1, sizeof(int64_t));

    int64_t *e4_2 = (int64_t *)calloc(max_n + 1, sizeof(int64_t));
    int64_t *e4_3 = (int64_t *)calloc(max_n + 1, sizeof(int64_t));
    int64_t *e6_2 = (int64_t *)calloc(max_n + 1, sizeof(int64_t));
    int64_t *e4_e6 = (int64_t *)calloc(max_n + 1, sizeof(int64_t));
    int64_t *e4_2_e6 = (int64_t *)calloc(max_n + 1, sizeof(int64_t));

    int64_t *delta = (int64_t *)calloc(max_n + 1, sizeof(int64_t));
    int64_t *t2_delta = (int64_t *)calloc(max_n + 1, sizeof(int64_t));
    int64_t *t3_delta = (int64_t *)calloc(max_n + 1, sizeof(int64_t));

    if (!e4 || !e6 || !e8 || !e10 || !e14 || !e4_2 || !e4_3 || !e6_2 || 
        !e4_e6 || !e4_2_e6 || !delta || !t2_delta || !t3_delta) {
        fprintf(stderr, "Помилка виділення динамічної пам'яті\n");
        free(e4); free(e6); free(e8); free(e10); free(e14);
        free(e4_2); free(e4_3); free(e6_2); free(e4_e6); free(e4_2_e6);
        free(delta); free(t2_delta); free(t3_delta);
        return 1;
    }

    /* 1. Генерація рядів Ейзенштейна E4, E6, E8, E10, E14 */
    e4[0] = 1;
    e6[0] = 1;
    e8[0] = 1;
    e10[0] = 1;
    e14[0] = 1;
    for (size_t n = 1; n <= max_n; ++n) {
        e4[n] = 240 * (int64_t)sum_divisor_powers((uint32_t)n, 3);
        e6[n] = -504 * (int64_t)sum_divisor_powers((uint32_t)n, 5);
        e8[n] = 480 * (int64_t)sum_divisor_powers((uint32_t)n, 7);
        e10[n] = -264 * (int64_t)sum_divisor_powers((uint32_t)n, 9);
        e14[n] = -24 * (int64_t)sum_divisor_powers((uint32_t)n, 13);
    }

    /* 2. Обчислення добутків рядів */
    multiply_series(e4, e4, e4_2, max_n);
    multiply_series(e4_2, e4, e4_3, max_n);
    multiply_series(e6, e6, e6_2, max_n);
    multiply_series(e4, e6, e4_e6, max_n);
    multiply_series(e4_2, e6, e4_2_e6, max_n);

    /* 3. Перевірка алгебраїчних тотожностей у просторах M_k */
    printf("=== Перевірка тотожностей у кільці M_*(SL(2, Z)) ===\n");
    bool ok_e8 = compare_series(e8, e4_2, max_n);
    printf("  1. E8 == E4^2:            %s\n", ok_e8 ? "ПІДТВЕРДЖЕНО" : "ПОМИЛКА");

    bool ok_e10 = compare_series(e10, e4_e6, max_n);
    printf("  2. E10 == E4 * E6:        %s\n", ok_e10 ? "ПІДТВЕРДЖЕНО" : "ПОМИЛКА");

    bool ok_e14 = compare_series(e14, e4_2_e6, max_n);
    printf("  3. E14 == E4^2 * E6:      %s\n\n", ok_e14 ? "ПІДТВЕРДЖЕНО" : "ПОМИЛКА");

    /* 4. Обчислення параболічного дискримінанта Delta = (E4^3 - E6^2) / 1728 */
    for (size_t n = 0; n <= max_n; ++n) {
        delta[n] = (e4_3[n] - e6_2[n]) / 1728;
    }

    printf("=== Коефіцієнти Фур'є E4, E6 та Delta (функція Рамануджана tau(n)) ===\n");
    printf("n\tE4(n)\t\tE6(n)\t\tDelta(n) [tau(n)]\n");
    printf("------------------------------------------------------------------\n");
    for (size_t n = 1; n <= max_n; ++n) {
        printf("%zu\t%lld\t\t%lld\t\t%lld\n", n, (long long)e4[n], (long long)e6[n], (long long)delta[n]);
    }

    /* 5. Дія операторів Гекке T_2 та T_3 на параболічну форму Delta (вага k = 12) */
    apply_hecke_operator(delta, t2_delta, max_n, 2, 12);
    apply_hecke_operator(delta, t3_delta, max_n, 3, 12);

    printf("\n=== Перевірка дії оператора Гекке T_2 на Delta (tau(2) = %lld) ===\n", (long long)delta[2]);
    printf("n\ttau(n)\t\tT_2(Delta)[n]\ttau(2)*tau(n)\tРезультат\n");
    printf("------------------------------------------------------------------\n");
    for (size_t n = 1; n <= 5; ++n) {
        int64_t expected = delta[2] * delta[n];
        printf("%zu\t%lld\t\t%lld\t\t%lld\t\t%s\n", 
               n, (long long)delta[n], (long long)t2_delta[n], (long long)expected,
               (t2_delta[n] == expected) ? "ЗБІГАЄТЬСЯ" : "ПОМИЛКА");
    }

    printf("\n=== Перевірка дії оператора Гекке T_3 на Delta (tau(3) = %lld) ===\n", (long long)delta[3]);
    printf("n\ttau(n)\t\tT_3(Delta)[n]\ttau(3)*tau(n)\tРезультат\n");
    printf("------------------------------------------------------------------\n");
    for (size_t n = 1; n <= 3; ++n) {
        int64_t expected = delta[3] * delta[n];
        printf("%zu\t%lld\t\t%lld\t\t%lld\t\t%s\n", 
               n, (long long)delta[n], (long long)t3_delta[n], (long long)expected,
               (t3_delta[n] == expected) ? "ЗБІГАЄТЬСЯ" : "ПОМИЛКА");
    }

    /* 6. Перевірка мультиплікативних тотожностей Рамануджана */
    printf("\n=== Перевірка мультиплікативних властивостей функції Рамануджана ===\n");
    int64_t tau6 = delta[6];
    int64_t tau2_tau3 = delta[2] * delta[3];
    printf("  tau(6) = %lld,  tau(2)*tau(3) = %lld  ==> %s\n",
           (long long)tau6, (long long)tau2_tau3,
           (tau6 == tau2_tau3) ? "МУЛЬТИПЛІКАТИВНІСТЬ ПІДТВЕРДЖЕНО" : "ПОМИЛКА");

    int64_t tau10 = delta[10];
    int64_t tau2_tau5 = delta[2] * delta[5];
    printf("  tau(10) = %lld, tau(2)*tau(5) = %lld ==> %s\n",
           (long long)tau10, (long long)tau2_tau5,
           (tau10 == tau2_tau5) ? "МУЛЬТИПЛІКАТИВНІСТЬ ПІДТВЕРДЖЕНО" : "ПОМИЛКА");

    /* Перевірка рекурентності для степеня простого числа: tau(4) = tau(2)^2 - 2^11 * tau(1) */
    int64_t tau4_expected = delta[2] * delta[2] - 2048 * delta[1];
    printf("  tau(4) = %lld, tau(2)^2 - 2^11*tau(1) = %lld ==> %s\n",
           (long long)delta[4], (long long)tau4_expected,
           (delta[4] == tau4_expected) ? "СТЕПЕНЕВА ТОТОЖНІСТЬ ПІДТВЕРДЖЕНА" : "ПОМИЛКА");

    /* 7. Перевірка межі Деліня: |tau(p)| <= 2 * p^(11/2) */
    printf("\n=== Перевірка гіпотези Рамануджана (межа Деліня) ===\n");
    uint32_t primes[] = {2, 3, 5, 7};
    for (size_t i = 0; i < 4; ++i) {
        uint32_t p = primes[i];
        double bound = 2.0 * pow((double)p, 5.5);
        int64_t val = delta[p];
        printf("  p = %u: |tau(%u)| = %lld, 2*p^(11/2) = %.2f ==> %s\n",
               p, p, (long long)llabs(val), bound,
               ((double)llabs(val) <= bound) ? "МЕЖА ДЕЛІНЯ ВИКОНУЄТЬСЯ" : "ПОРУШЕННЯ МЕЖІ");
    }

    /* Очищення динамічно виділеної пам'яті */
    free(e4); free(e6); free(e8); free(e10); free(e14);
    free(e4_2); free(e4_3); free(e6_2); free(e4_e6); free(e4_2_e6);
    free(delta); free(t2_delta); free(t3_delta);
    return 0;
}
