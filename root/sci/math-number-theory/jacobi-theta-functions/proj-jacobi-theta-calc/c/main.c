#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

/* Пряме підсумовування тета-константи theta3(q) для малих q */
double theta3_direct(double q, double eps) {
    if (q <= 0.0) return 1.0;
    
    double sum = 1.0;
    double term;
    int n = 1;
    
    do {
        term = 2.0 * pow(q, (double)(n * n));
        sum += term;
        n++;
    } while (term > eps && n < 1000);
    
    return sum;
}

/* Адаптивне обчислення theta3(q) з модулярним перетворенням Якобі */
double theta3_adaptive(double q, double eps) {
    if (q <= 0.0) return 1.0;
    if (q >= 1.0) return INFINITY;
    
    /* Якщо q > 0.6, виконуємо перетворення Якобі t -> 1/t */
    if (q > 0.6) {
        double t = -log(q) / M_PI;
        double q_prime = exp(-M_PI / t);
        double theta_prime = theta3_direct(q_prime, eps);
        return (1.0 / sqrt(t)) * theta_prime;
    }
    
    return theta3_direct(q, eps);
}

/* Обчислення повного еліптичного інтеграла K(k) через AGM */
double elliptic_k_agm(double k, double eps) {
    if (k < 0.0 || k >= 1.0) return INFINITY;
    
    double a = 1.0;
    double b = sqrt(1.0 - k * k);
    
    while (fabs(a - b) > eps) {
        double a_next = 0.5 * (a + b);
        double b_next = sqrt(a * b);
        a = a_next;
        b = b_next;
    }
    
    return M_PI / (2.0 * a);
}

int main(void) {
    double q_values[] = {0.1, 0.5, 0.9, 0.999, 0.99999};
    size_t count = sizeof(q_values) / sizeof(q_values[0]);
    double eps = 1e-15;
    
    printf("=== Обчислення тета-константи theta3(q) ===\n");
    for (size_t i = 0; i < count; i++) {
        double q = q_values[i];
        double res = theta3_adaptive(q, eps);
        printf("q = %-8.5f | theta3(q) = %-18.12f\n", q, res);
    }
    
    printf("\n=== Перевірка еліптичного інтеграла K(k) через AGM ===\n");
    double k = 0.5;
    double K_val = elliptic_k_agm(k, eps);
    printf("k = %.2f | K(k) = %.12f\n", k, K_val);
    
    return 0;
}
