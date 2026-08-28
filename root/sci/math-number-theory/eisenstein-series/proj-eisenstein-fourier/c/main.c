#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <complex.h>
#include <stdint.h>

#define PI 3.14159265358979323846

/* Обчислення суми дільників sigma_k(n) = sum_{d|n} d^k для одного числа n */
uint64_t compute_sigma_single(uint32_t n, uint32_t k) {
    uint64_t sum = 0;
    for (uint32_t d = 1; d * d <= n; d++) {
        if (n % d == 0) {
            uint64_t term1 = 1;
            for (uint32_t p = 0; p < k; p++) term1 *= d;
            sum += term1;

            uint32_t d2 = n / d;
            if (d2 != d) {
                uint64_t term2 = 1;
                for (uint32_t p = 0; p < k; p++) term2 *= d2;
                sum += term2;
            }
        }
    }
    return sum;
}

/* Обчислення масиву сум дільників за допомогою решета для n від 1 до max_n */
void compute_sigma_sieve(uint32_t max_n, uint32_t k, uint64_t *sigma) {
    for (uint32_t i = 1; i <= max_n; i++) {
        sigma[i] = 0;
    }
    for (uint32_t d = 1; d <= max_n; d++) {
        uint64_t d_pow = 1;
        for (uint32_t p = 0; p < k; p++) d_pow *= d;

        for (uint32_t mult = d; mult <= max_n; mult += d) {
            sigma[mult] += d_pow;
        }
    }
}

/* Генерація коефіцієнтів q-розкладу для E4(q) та E6(q) до макс індексу max_n */
void generate_eisenstein_q_expansion(uint32_t max_n, int64_t *e4, int64_t *e6) {
    uint64_t *s3 = (uint64_t *)calloc(max_n + 1, sizeof(uint64_t));
    uint64_t *s5 = (uint64_t *)calloc(max_n + 1, sizeof(uint64_t));

    if (!s3 || !s5) {
        free(s3);
        free(s5);
        return;
    }

    compute_sigma_sieve(max_n, 3, s3);
    compute_sigma_sieve(max_n, 5, s5);

    e4[0] = 1;
    e6[0] = 1;

    for (uint32_t n = 1; n <= max_n; n++) {
        e4[n] = (int64_t)(240 * s3[n]);
        e6[n] = (int64_t)(-504 * s5[n]);
    }

    free(s3);
    free(s5);
}

/* Обчислення коефіцієнтів дискримінантної форми Delta(q) = (E4^3 - E6^2) / 1728 */
void generate_ramanujan_tau(uint32_t max_n, const int64_t *e4, const int64_t *e6, int64_t *tau) {
    int64_t *e4_sq   = (int64_t *)calloc(max_n + 1, sizeof(int64_t));
    int64_t *e4_cube = (int64_t *)calloc(max_n + 1, sizeof(int64_t));
    int64_t *e6_sq   = (int64_t *)calloc(max_n + 1, sizeof(int64_t));

    if (!e4_sq || !e4_cube || !e6_sq) {
        free(e4_sq);
        free(e4_cube);
        free(e6_sq);
        return;
    }

    /* Множення поліномів: E4 * E4 */
    for (uint32_t i = 0; i <= max_n; i++) {
        for (uint32_t j = 0; j <= max_n - i; j++) {
            e4_sq[i + j] += e4[i] * e4[j];
        }
    }

    /* Множення поліномів: E4^2 * E4 */
    for (uint32_t i = 0; i <= max_n; i++) {
        for (uint32_t j = 0; j <= max_n - i; j++) {
            e4_cube[i + j] += e4_sq[i] * e4[j];
        }
    }

    /* Множення поліномів: E6 * E6 */
    for (uint32_t i = 0; i <= max_n; i++) {
        for (uint32_t j = 0; j <= max_n - i; j++) {
            e6_sq[i + j] += e6[i] * e6[j];
        }
    }

    /* Delta = (E4^3 - E6^2) / 1728 */
    for (uint32_t n = 0; n <= max_n; n++) {
        int64_t diff = e4_cube[n] - e6_sq[n];
        tau[n] = diff / 1728;
    }

    free(e4_sq);
    free(e4_cube);
    free(e6_sq);
}

/* Оцінка ряду E4(tau) в точці tau з верхньої півплощини H */
double complex eval_e4(double complex tau, uint32_t terms) {
    if (cimag(tau) <= 0.0) {
        fprintf(stderr, "Помилка: tau має бути у Верхній півплощині (Im(tau) > 0).\n");
        return 0.0 + 0.0 * I;
    }

    double complex q = cexp(2.0 * PI * I * tau);
    double complex sum = 1.0 + 0.0 * I;
    double complex q_pow = q;

    for (uint32_t n = 1; n <= terms; n++) {
        uint64_t s3 = compute_sigma_single(n, 3);
        sum += (double)(240 * s3) * q_pow;
        q_pow *= q;

        if (cabs(q_pow) < 1e-15) break;
    }

    return sum;
}

int main(void) {
    uint32_t N = 10;
    int64_t e4[11], e6[11], tau[11];

    generate_eisenstein_q_expansion(N, e4, e6);
    generate_ramanujan_tau(N, e4, e6, tau);

    printf("--- Коефіцієнти q-розкладу рядів Ейзенштейна та функції Рамануджана ---\n");
    printf("n  | E4(n)        | E6(n)        | Tau(n) (Рамануджан)\n");
    printf("---|--------------|--------------|--------------------\n");
    for (uint32_t n = 0; n <= N; n++) {
        printf("%-2u | %-12lld | %-12lld | %-18lld\n", n, (long long)e4[n], (long long)e6[n], (long long)tau[n]);
    }

    double complex tau_val = 0.0 + 1.0 * I;
    double complex val_e4 = eval_e4(tau_val, 50);

    printf("\nОцінка E4(i) = %.10f + %.10fi\n", creal(val_e4), cimag(val_e4));

    return 0;
}
