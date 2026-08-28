#include <stdio.h>
#include <math.h>

/* Точне додавання двох чисел за алгоритмом TwoSum (Knuth) */
static inline void two_sum(double a, double b, double *s, double *t) {
    *s = a + b;
    double b_virtual = *s - a;
    double a_virtual = *s - b_virtual;
    double b_err = b - b_virtual;
    double a_err = a - a_virtual;
    *t = a_err + b_err;
}

/* Точне множення двох чисел за допомогою FMA (TwoProduct) */
static inline void two_prod_fma(double a, double b, double *p, double *e) {
    *p = a * b;
    *e = fma(a, b, -(*p));
}

/* Компенсована схема Горнера */
double compensated_horner(const double *a, size_t n, double x0) {
    double s = a[0];
    double c = 0.0;

    for (size_t i = 1; i <= n; ++i) {
        double p, pi;
        two_prod_fma(s, x0, &p, &pi);

        double s_new, sigma;
        two_sum(p, a[i], &s_new, &sigma);

        s = s_new;
        c = c * x0 + (pi + sigma);
    }

    return s + c;
}

int main(void) {
    /* P(x) = (x - 1)^6 = x^6 - 6x^5 + 15x^4 - 20x^3 + 15x^2 - 6x + 1 у точці x = 1.000001 */
    double coeffs[] = {1.0, -6.0, 15.0, -20.0, 15.0, -6.0, 1.0};
    size_t n = 6;
    double x0 = 1.000001;

    double comp_val = compensated_horner(coeffs, n, x0);

    printf("Компенсоване значення: %.16e\n", comp_val);
    printf("Точне значення (x-1)^6: %.16e\n", pow(x0 - 1.0, 6.0));

    return 0;
}
