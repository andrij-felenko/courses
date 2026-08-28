#include <stddef.h>
#include <math.h>

/* Компенсований скалярний добуток Dot2 */
double dot2(const double* x, const double* y, size_t n) {
    if (n == 0) return 0.0;
    double p = x[0] * y[0];
    double s = p;
    double c = fma(x[0], y[0], -p);

    for (size_t i = 1; i < n; ++i) {
        double pi = x[i] * y[i];
        double pi_err = fma(x[i], y[i], -pi);

        /* TwoSum для акумуляції суми */
        double s_next = s + pi;
        double v = s_next - s;
        double s_err = (s - (s_next - v)) + (pi - v);

        s = s_next;
        c += (s_err + pi_err);
    }
    return s + c;
}
