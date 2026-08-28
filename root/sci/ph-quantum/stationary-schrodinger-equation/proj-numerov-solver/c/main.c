#include <stdio.h>
#include <stdlib.h>
#include <math.h>

/* Безрозмірний потенціал гармонічного осцилятора: V(x) = 0.5 * x^2 */
static double potential_harmonic(double x) {
    return 0.5 * x * x;
}

/* Обчислення хвильового числа k^2(x) = 2 * (E - V(x)) у безрозмірних одиницях (m=1, hbar=1) */
static double k2_val(double E, double x) {
    return 2.0 * (E - potential_harmonic(x));
}

/* Інтегрування методом Нумерова від x_min до x_max при заданій енергії E.
   Повертає значення хвильової функції на правому кінці сітки. */
double numerov_integrate(double E, double x_min, double x_max, int steps, double *psi_out) {
    double h = (x_max - x_min) / steps;
    double h2 = h * h;
    double h2_12 = h2 / 12.0;

    /* Початкові умови на лівій межі: ψ(x_min) = 0, ψ(x_min + h) = 1e-7 */
    psi_out[0] = 0.0;
    psi_out[1] = 1e-7;

    for (int i = 1; i < steps; ++i) {
        double x_prev = x_min + (i - 1) * h;
        double x_curr = x_min + i * h;
        double x_next = x_min + (i + 1) * h;

        double k2_prev = k2_val(E, x_prev);
        double k2_curr = k2_val(E, x_curr);
        double k2_next = k2_val(E, x_next);

        double term_curr = 2.0 * (1.0 - 5.0 * h2_12 * k2_curr) * psi_out[i];
        double term_prev = (1.0 + h2_12 * k2_prev) * psi_out[i - 1];
        double denom = 1.0 + h2_12 * k2_next;

        psi_out[i + 1] = (term_curr - term_prev) / denom;
    }

    return psi_out[steps];
}

/* Пошук власного значення енергії методом бісекції */
double find_eigenvalue(double E_low, double E_high, double x_min, double x_max, int steps, double tol) {
    double *psi = (double *)malloc((steps + 1) * sizeof(double));
    if (!psi) {
        fprintf(stderr, "Помилка виділення пам'яті!\n");
        return -1.0;
    }

    double f_low = numerov_integrate(E_low, x_min, x_max, steps, psi);
    double f_high = numerov_integrate(E_high, x_min, x_max, steps, psi);

    if (f_low * f_high > 0.0) {
        fprintf(stderr, "Інтервал [E_low, E_high] не містить кореня!\n");
        free(psi);
        return -1.0;
    }

    double E_mid = E_low;
    while ((E_high - E_low) > tol) {
        E_mid = 0.5 * (E_low + E_high);
        double f_mid = numerov_integrate(E_mid, x_min, x_max, steps, psi);

        if (fabs(f_mid) < 1e-12) {
            break;
        }

        if (f_low * f_mid < 0.0) {
            E_high = E_mid;
            f_high = f_mid;
        } else {
            E_low = E_mid;
            f_low = f_mid;
        }
    }

    free(psi);
    return E_mid;
}

int main(void) {
    double x_min = -5.0;
    double x_max = 5.0;
    int steps = 1000;
    double tol = 1e-7;

    printf("Пошук перших трьох власних значень квантового осцилятора:\n");

    /* Пошук точних аналітичних значень 0.5, 1.5, 2.5 */
    double E0 = find_eigenvalue(0.1, 0.9, x_min, x_max, steps, tol);
    double E1 = find_eigenvalue(1.1, 1.9, x_min, x_max, steps, tol);
    double E2 = find_eigenvalue(2.1, 2.9, x_min, x_max, steps, tol);

    printf("E0 (основний стан) = %.6f (теоретичне: 0.500000)\n", E0);
    printf("E1 (1-й збуджений) = %.6f (теоретичне: 1.500000)\n", E1);
    printf("E2 (2-й збуджений) = %.6f (теоретичне: 2.500000)\n", E2);

    return 0;
}
