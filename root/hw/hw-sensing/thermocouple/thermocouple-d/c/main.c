#include <stdint.h>
#include <stdbool.h>

/* Коефіцієнти оберненого полінома NIST Type K для діапазону 0..500 °C (мВ -> °C) */
static const double K_INV_POLY_0_500[] = {
    0.000000E+00,  2.508355E+01,  7.860106E-02,
   -2.503131E-01,  8.315270E-02, -1.228034E-02,
    9.804036E-04, -4.413030E-05,  1.057734E-06,
   -1.052755E-08
};

/* Схема Горнера: P(v) = d[0] + v*(d[1] + v*(d[2] + ...)) */
double evaluate_nist_inverse_type_k(double mv_total) {
    const size_t n = sizeof(K_INV_POLY_0_500) / sizeof(K_INV_POLY_0_500[0]);
    double temp = K_INV_POLY_0_500[n - 1];
    for (size_t i = n - 1; i > 0; --i) {
        temp = temp * mv_total + K_INV_POLY_0_500[i - 1];
    }
    return temp;
}
