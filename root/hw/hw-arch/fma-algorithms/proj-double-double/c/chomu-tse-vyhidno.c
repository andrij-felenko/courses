#include <stddef.h>
#include <math.h>

/* Компенсований скалярний добуток Огіти-Румпа-Оїші (Dot2) */
double comp_dot_product(const double* x, const double* y, size_t n) {
    if (n == 0) return 0.0;

    eft_pair_t p = two_prod_fma(x[0], y[0]);
    double s = p.val;
    double c = p.err;

    for (size_t i = 1; i < n; ++i) {
        eft_pair_t prod = two_prod_fma(x[i], y[i]);
        eft_pair_t sum = two_sum(s, prod.val);
        s = sum.val;
        c += (sum.err + prod.err);
    }

    return s + c;
}

/* Компенсована схема Горнера для обчислення полінома: P(x) = sum(a[i] * x^i) */
double comp_horner(const double* a, size_t degree, double x) {
    if (degree == 0) return a[0];

    double s = a[degree];
    double c = 0.0;

    for (size_t k = degree; k > 0; --k) {
        size_t i = k - 1;
        eft_pair_t prod = two_prod_fma(s, x);
        eft_pair_t sum = two_sum(prod.val, a[i]);
        s = sum.val;
        double err_step = prod.err + sum.err;
        c = fma(c, x, err_step);
    }

    return s + c;
}
