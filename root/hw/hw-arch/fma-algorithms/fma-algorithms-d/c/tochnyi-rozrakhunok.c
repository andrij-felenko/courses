#include <math.h>

/* Точний розрахунок дискримінанта квадратного рівняння D = b^2 - 4ac */
double accurate_discriminant(double a, double b, double c) {
    double four_a = 4.0 * a;
    double p = four_a * c;
    double dp = fma(four_a, c, -p);
    double d = fma(b, b, -p);
    return d - dp;
}
