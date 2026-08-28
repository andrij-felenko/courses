#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

/* Обчислення суми Чебишова алгоритмом Кленшоу */
double clenshaw_eval(const double *coeffs, int n, double x) {
    if (n <= 0) return 0.0;
    if (n == 1) return coeffs[0] * 0.5;

    double b_k1 = 0.0; /* b_{k+1} */
    double b_k2 = 0.0; /* b_{k+2} */

    for (int k = n - 1; k >= 1; k--) {
        double b_k = 2.0 * x * b_k1 - b_k2 + coeffs[k];
        b_k2 = b_k1;
        b_k1 = b_k;
    }

    return x * b_k1 - b_k2 + 0.5 * coeffs[0];
}

/* Обчислення коефіцієнтів інтерполяційного полінома Чебишова */
void fit_chebyshev_series(double (*func)(double), int n, double *coeffs) {
    double *nodes = (double *)malloc(sizeof(double) * n);
    double *f_vals = (double *)malloc(sizeof(double) * n);

    for (int k = 0; k < n; k++) {
        nodes[k] = cos((2.0 * (k + 1) - 1.0) * M_PI / (2.0 * n));
        f_vals[k] = func(nodes[k]);
    }

    for (int m = 0; m < n; m++) {
        double sum = 0.0;
        for (int k = 0; k < n; k++) {
            double t_mk = cos(m * (2.0 * k + 1.0) * M_PI / (2.0 * n));
            sum += f_vals[k] * t_mk;
        }
        coeffs[m] = (2.0 / n) * sum;
    }

    free(nodes);
    free(f_vals);
}

static double runge_function(double x) {
    return 1.0 / (1.0 + 25.0 * x * x);
}

int main(void) {
    const int N = 11;
    double coeffs[11];

    fit_chebyshev_series(runge_function, N, coeffs);

    const double test_points[] = {-0.95, -0.5, 0.0, 0.5, 0.95};
    const int num_pts = sizeof(test_points) / sizeof(test_points[0]);

    printf("%8s | %15s | %15s | %12s\n", "x", "Exact", "Approx", "Error");
    printf("----------------------------------------------------------\n");

    for (int i = 0; i < num_pts; i++) {
        double pt = test_points[i];
        double exact = runge_function(pt);
        double approx = clenshaw_eval(coeffs, N, pt);
        double err = fabs(exact - approx);
        printf("%8.2f | %15.8f | %15.8f | %12.4e\n", pt, exact, approx, err);
    }

    return 0;
}
