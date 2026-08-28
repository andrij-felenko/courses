#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

// Структура комплексного числа для мови C
typedef struct {
    double real;
    double imag;
} Complex;

static Complex c_add(Complex a, Complex b) {
    return (Complex){a.real + b.real, a.imag + b.imag};
}

static Complex c_mul(Complex a, Complex b) {
    return (Complex){a.real * b.real - a.imag * b.imag, a.real * b.imag + a.imag * b.real};
}

static Complex c_exp_i(double phi) {
    return (Complex){cos(phi), sin(phi)};
}

static double c_abs_sq(Complex a) {
    return a.real * a.real + a.imag * a.imag;
}

// Одномірне ДПФ (для спрощення без зовнішніх бібліотек)
static void dft(const Complex* in, Complex* out, int N, int sign) {
    for (int k = 0; k < N; k++) {
        out[k] = (Complex){0.0, 0.0};
        for (int n = 0; n < N; n++) {
            double angle = sign * 2.0 * M_PI * k * n / N;
            Complex w = c_exp_i(angle);
            out[k] = c_add(out[k], c_mul(in[n], w));
        }
        if (sign < 0) {
            out[k].real /= N;
            out[k].imag /= N;
        }
    }
}

int main(void) {
    const int N = 256;
    const double L = 100.0;
    const double dx = L / N;
    const double dt = 0.05;
    const int steps = 400;

    const double m = 1.0;
    const double hbar = 1.0;

    // Параметри бар'єра
    const double x_b1 = 48.0;
    const double x_b2 = 52.0;
    const double V0 = 1.5;

    // Параметри хвильового пакета
    const double x0 = 25.0;
    const double sigma = 4.0;
    const double E0 = 1.0;
    const double k0 = sqrt(2.0 * m * E0) / hbar;

    Complex* psi = (Complex*)malloc(N * sizeof(Complex));
    Complex* psi_k = (Complex*)malloc(N * sizeof(Complex));
    double* V = (double*)malloc(N * sizeof(double));

    if (!psi || !psi_k || !V) {
        fprintf(stderr, "Помилка виділення пам'яті\n");
        free(psi); free(psi_k); free(V);
        return 1;
    }

    // Ініціалізація потенціалу та хвильової функції
    double norm_factor = 1.0 / sqrt(sigma * sqrt(M_PI));
    for (int i = 0; i < N; i++) {
        double x = i * dx;
        V[i] = (x >= x_b1 && x <= x_b2) ? V0 : 0.0;

        double g = exp(-(x - x0) * (x - x0) / (2.0 * sigma * sigma));
        psi[i] = c_mul((Complex){g * norm_factor, 0.0}, c_exp_i(k0 * x));
    }

    // Головний цикл еволюції у часі (Split-Operator)
    for (int step = 0; step < steps; step++) {
        // 1. Половина кроку потенціалу exp(-i V dt / 2 hbar)
        for (int i = 0; i < N; i++) {
            double phase = -V[i] * dt / (2.0 * hbar);
            psi[i] = c_mul(psi[i], c_exp_i(phase));
        }

        // 2. Перехід в імпульсний простір
        dft(psi, psi_k, N, 1);

        // 3. Крок кінетичної енергії в k-просторі
        for (int k = 0; k < N; k++) {
            double k_val = (k < N / 2) ? (2.0 * M_PI * k / L) : (2.0 * M_PI * (k - N) / L);
            double phase = - (hbar * k_val * k_val / (2.0 * m)) * dt;
            psi_k[k] = c_mul(psi_k[k], c_exp_i(phase));
        }

        // 4. Повернення в координатний простір
        dft(psi_k, psi, N, -1);

        // 5. Друга половина кроку потенціалу
        for (int i = 0; i < N; i++) {
            double phase = -V[i] * dt / (2.0 * hbar);
            psi[i] = c_mul(psi[i], c_exp_i(phase));
        }
    }

    // Розрахунок R та T
    double R = 0.0, T = 0.0;
    for (int i = 0; i < N; i++) {
        double x = i * dx;
        double prob = c_abs_sq(psi[i]) * dx;
        if (x < x_b1) R += prob;
        else if (x > x_b2) T += prob;
    }

    printf("=== Результати чисельного симулятора тунелювання (C) ===\n");
    printf("Енергія пакета E0: %.2f | Висота бар'єра V0: %.2f\n", E0, V0);
    printf("Коефіцієнт відбивання R: %.4f\n", R);
    printf("Коефіцієнт проходження (тунелювання) T: %.4f\n", T);
    printf("Сума ймовірностей R + T: %.4f\n", R + T);

    free(psi);
    free(psi_k);
    free(V);
    return 0;
}
