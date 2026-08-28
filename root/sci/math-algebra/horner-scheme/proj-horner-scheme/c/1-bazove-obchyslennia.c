#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

/* 
 * Обчислення значення многочлена P(x) = a[n]*x^n + ... + a[0] у точці x0.
 * a: масив коефіцієнтів довжиною n + 1 (від старшого a[n] до молодшого a[0])
 * n: степінь багаточлена
 */
double horner_eval(const double *a, size_t n, double x0) {
    double result = a[0]; /* a[n] у зворотному порядку, або a[n] при індексації */
    for (size_t i = 1; i <= n; ++i) {
        result = result * x0 + a[i];
    }
    return result;
}

/*
 * Синтетичне ділення P(x) на (x - x0).
 * Заповнює масив q коефіцієнтами частки Q(x) степеня n - 1 (розмір n).
 * Повертає остачу R = P(x0).
 */
double horner_synthetic_div(const double *a, size_t n, double x0, double *q) {
    q[0] = a[0];
    for (size_t i = 1; i < n; ++i) {
        q[i] = a[i] + x0 * q[i - 1];
    }
    return a[n] + x0 * q[n - 1];
}

int main(void) {
    /* P(x) = 2x³ - 6x² + 2x - 1, степінь n = 3, коефіцієнти від a3 до a0 */
    double coeffs[] = {2.0, -6.0, 2.0, -1.0};
    size_t n = 3;
    double x0 = 3.0;

    double val = horner_eval(coeffs, n, x0);
    printf("P(%.1f) = %.2f\n", x0, val);

    double q[3];
    double rem = horner_synthetic_div(coeffs, n, x0, q);
    printf("Остача R = %.2f\n", rem);
    printf("Частка Q(x) = %.1fx² + %.1fx + %.1f\n", q[0], q[1], q[2]);

    return 0;
}
