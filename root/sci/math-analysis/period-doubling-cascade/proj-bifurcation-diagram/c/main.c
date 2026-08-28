#include <stdio.h>
#include <math.h>
#include <stdlib.h>

static double logistic(double x, double r) {
    return r * x * (1.0 - x);
}

static double logistic_derivative_r(double x, double r, double w) {
    return r * (1.0 - 2.0 * x) * w + x * (1.0 - x);
}

static double find_superstable_r(int n, double r_guess) {
    int period = 1 << n; // 2^n
    double r = r_guess;
    int iter;

    for (iter = 0; iter < 100; ++iter) {
        double x = 0.5;
        double w = 0.0; // dx/dr
        int k;

        for (k = 0; k < period; ++k) {
            w = logistic_derivative_r(x, r, w);
            x = logistic(x, r);
        }

        double f_val = x - 0.5;
        double f_prime = w;

        if (fabs(f_val) < 1e-13) {
            break;
        }

        r = r - f_val / f_prime;
    }

    return r;
}

static double calculate_lyapunov(double r, int num_iters) {
    double x = 0.5;
    int i;
    for (i = 0; i < 1000; ++i) {
        x = logistic(x, r);
    }

    double sum_log = 0.0;
    for (i = 0; i < num_iters; ++i) {
        double deriv = fabs(r * (1.0 - 2.0 * x));
        if (deriv < 1e-12) deriv = 1e-12;
        sum_log += log(deriv);
        x = logistic(x, r);
    }

    return sum_log / num_iters;
}

int main(void) {
    double guesses[6] = {2.0, 3.2, 3.498, 3.5546, 3.56666, 3.56924};
    double R_vals[6];
    int i;

    printf("=== Обчислення надстійких точок (C) ===\n");
    for (i = 0; i < 6; ++i) {
        R_vals[i] = find_superstable_r(i, guesses[i]);
        printf("R_%d = %.12f\n", i, R_vals[i]);
    }

    printf("\n=== Обчислення сталої delta (C) ===\n");
    for (i = 1; i < 5; ++i) {
        double delta = (R_vals[i] - R_vals[i-1]) / (R_vals[i+1] - R_vals[i]);
        printf("delta_%d = %.12f\n", i, delta);
    }

    return 0;
}
