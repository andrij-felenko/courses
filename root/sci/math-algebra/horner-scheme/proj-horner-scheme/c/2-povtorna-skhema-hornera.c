#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/*
 * Обчислює значення многочлена та його похідних P(x0), P'(x0), P''(x0)/2!, ..., P^(n)(x0)/n!
 * Вхідний масив a скопійовано у робочий буфер, тому вхідні дані не змінюються.
 * Результат записується у derivs[0..n], де derivs[k] = P^(k)(x0) / k!
 */
void horner_taylor_coefficients(const double *a, size_t n, double x0, double *derivs) {
    double *work = (double *)malloc((n + 1) * sizeof(double));
    if (!work) return;

    memcpy(work, a, (n + 1) * sizeof(double));

    /* Повторні проходи за схемою Горнера */
    for (size_t k = 0; k <= n; ++k) {
        for (size_t i = 0; i < n - k; ++i) {
            work[i + 1] += x0 * work[i];
        }
        derivs[k] = work[n - k];
    }

    free(work);
}

int main(void) {
    /* P(x) = x³ - 3x² + 3x - 1 = (x - 1)³ */
    double coeffs[] = {1.0, -3.0, 3.0, -1.0}; /* від a3 до a0 */
    size_t n = 3;
    double x0 = 2.0;

    double derivs[4];
    horner_taylor_coefficients(coeffs, n, x0, derivs);

    printf("Розклад Тейлора P(x) навколо x0 = %.1f:\n", x0);
    for (size_t k = 0; k <= n; ++k) {
        printf("P^(%zu)(%.1f) / %zu! = %.2f\n", k, x0, k, derivs[k]);
    }

    return 0;
}
