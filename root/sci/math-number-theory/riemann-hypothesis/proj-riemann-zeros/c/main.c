#include <stdio.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

/* Асимптотична фаза Рімана-Зігеля θ(t) */
double riemann_siegel_theta(double t) {
    if (t < 0.1) return 0.0;
    double t_2pi = t / (2.0 * M_PI);
    return (t / 2.0) * log(t_2pi) - (t / 2.0) - (M_PI / 8.0) + (1.0 / (48.0 * t));
}

/* Дійснозначна функція Харді Z(t) */
double hardy_z(double t) {
    double theta = riemann_siegel_theta(t);
    int bound = (int)sqrt(t / (2.0 * M_PI));
    if (bound < 1) bound = 1;

    double z_sum = 0.0;
    for (int n = 1; n <= bound; ++n) {
        z_sum += (1.0 / sqrt((double)n)) * cos(theta - t * log((double)n));
    }
    return 2.0 * z_sum;
}

/* Пошук нулів методом бісекції */
void find_riemann_zeros(double t_min, double t_max, double step, double tol) {
    double t_curr = t_min;
    double z_curr = hardy_z(t_curr);
    int count = 1;

    printf("Пошук нулів на інтервалі t ∈ [%.1f, %.1f]:\n", t_min, t_max);

    while (t_curr < t_max) {
        double t_next = t_curr + step;
        double z_next = hardy_z(t_next);

        if (z_curr * z_next < 0.0) {
            double low = t_curr;
            double high = t_next;
            double mid = low;

            for (int iter = 0; iter < 50; ++iter) {
                mid = (low + high) / 2.0;
                double z_mid = hardy_z(mid);
                if (fabs(z_mid) < tol || (high - low) / 2.0 < tol) {
                    break;
                }
                if (z_curr * z_mid < 0.0) {
                    high = mid;
                } else {
                    low = mid;
                    z_curr = z_mid;
                }
            }
            printf("Нуль #%d: t = %.6f  =>  s = 1/2 + i·%.6f\n", count++, mid, mid);
        }
        t_curr = t_next;
        z_curr = z_next;
    }
}

int main(void) {
    find_riemann_zeros(10.0, 30.0, 0.1, 1e-7);
    return 0;
}
