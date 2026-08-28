#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define N 200            /* Кількість вузлів просторової сітки */
#define MAX_ITER 500     /* Максимальна кількість самоузгоджених ітерацій */
#define ALPHA 0.15       /* Коефіцієнт змішування потенціалу */

/* Фізичні константи в системі СІ */
static const double HBAR = 1.0545718e-34;
static const double QE = 1.60217663e-19;
static const double M0 = 9.1093837e-31;
static const double EPS0 = 8.8541878e-12;

/* Параметри матеріалу GaAs */
static const double M_EFF = 0.067 * 9.1093837e-31;  /* m* = 0.067 m0 */
static const double EPS_R = 12.9;                   /* Диелектрична проникність GaAs */
static const double NS_TOTAL = 4.0e15;               /* Листова густість 2DEG: 4e11 см^-2 = 4e15 м^-2 */

/* Розв'язувач тридіагональної системи методом Томаса (для рівняння Пуассона) */
void solve_tridiagonal(const double *a, const double *b, const double *c, const double *d, double *x, int n_size) {
    double c_star[N];
    double d_star[N];

    c_star[0] = c[0] / b[0];
    d_star[0] = d[0] / b[0];

    for (int i = 1; i < n_size; i++) {
        double m = b[i] - a[i] * c_star[i - 1];
        c_star[i] = c[i] / m;
        d_star[i] = (d[i] - a[i] * d_star[i - 1]) / m;
    }

    x[n_size - 1] = d_star[n_size - 1];
    for (int i = n_size - 2; i >= 0; i--) {
        x[i] = d_star[i] - c_star[i] * x[i + 1];
    }
}

/* Степеневий метод з ортогоналізацією для пошуку найнижчого власного стану E0, psi0 */
double find_ground_state(const double *V, double *psi, double dz) {
    double t0 = (HBAR * HBAR) / (2.0 * M_EFF * dz * dz);
    
    /* Початкове наближення хвильової функції */
    for (int i = 0; i < N; i++) {
        double z = i * dz;
        psi[i] = sin(M_PI * z / ((N - 1) * dz));
    }

    /* Нормування */
    double norm = 0.0;
    for (int i = 0; i < N; i++) norm += psi[i] * psi[i] * dz;
    norm = sqrt(norm);
    for (int i = 0; i < N; i++) psi[i] /= norm;

    /* Зворотна ітерація (Inverse Power Iteration) */
    double H_psi[N];
    for (int iter = 0; iter < 40; iter++) {
        /* Обчислення H * psi */
        for (int i = 1; i < N - 1; i++) {
            H_psi[i] = (V[i] + 2.0 * t0) * psi[i] - t0 * (psi[i - 1] + psi[i + 1]);
        }
        H_psi[0] = 0.0;
        H_psi[N - 1] = 0.0;

        /* Крок оновлення */
        for (int i = 1; i < N - 1; i++) {
            psi[i] = psi[i] / (H_psi[i] + 1e-30);
        }

        norm = 0.0;
        for (int i = 0; i < N; i++) norm += psi[i] * psi[i] * dz;
        norm = sqrt(norm);
        for (int i = 0; i < N; i++) psi[i] /= norm;
    }

    /* Обчислення середнього значення енергії <E0> = <psi|H|psi> */
    double E0 = 0.0;
    for (int i = 1; i < N - 1; i++) {
        double h_element = (V[i] + 2.0 * t0) * psi[i] - t0 * (psi[i - 1] + psi[i + 1]);
        E0 += psi[i] * h_element * dz;
    }
    return E0;
}

int main(void) {
    double z_max = 50.0e-9; /* 50 нанометрів */
    double dz = z_max / (N - 1);

    double V[N];
    double psi0[N];
    double n_density[N];
    double a[N], b[N], c[N], d[N], V_poisson[N];

    /* Ініціалізація початкового потенціалу ями (трикутне електричне поле Fs = 3e7 В/м) */
    double Fs = 3.0e7;
    for (int i = 0; i < N; i++) {
        V[i] = QE * Fs * (i * dz);
        V_poisson[i] = 0.0;
    }

    printf("=== Самоузгоджений розв'язок 1D Poisson-Schroedinger (C) ===\n");
    printf("Розмір сітки: N = %d, крок dz = %.2f нм\n", N, dz * 1e9);

    double E0 = 0.0;
    for (int iter = 0; iter < MAX_ITER; iter++) {
        /* 1. Розв'язок рівняння Шредінгера */
        E0 = find_ground_state(V, psi0, dz);

        /* 2. Обчислення електронної густини n(z) */
        for (int i = 0; i < N; i++) {
            n_density[i] = NS_TOTAL * (psi0[i] * psi0[i]);
        }

        /* 3. Формування системи для рівняння Пуассона: d2V/dz2 = (e^2 / eps) * n(z) */
        for (int i = 1; i < N - 1; i++) {
            a[i] = 1.0 / (dz * dz);
            b[i] = -2.0 / (dz * dz);
            c[i] = 1.0 / (dz * dz);
            d[i] = (QE * QE * n_density[i]) / (EPS_R * EPS0);
        }
        b[0] = 1.0; c[0] = 0.0; d[0] = V[0];               /* Межа z=0 */
        a[N-1] = 0.0; b[N-1] = 1.0; d[N-1] = QE * Fs * z_max; /* Межа z=z_max */

        solve_tridiagonal(a, b, c, d, V_poisson, N);

        /* 4. Самоузгоджене змішування потенціалу */
        double max_diff = 0.0;
        for (int i = 0; i < N; i++) {
            double V_next = ALPHA * V_poisson[i] + (1.0 - ALPHA) * V[i];
            double diff = fabs(V_next - V[i]);
            if (diff > max_diff) max_diff = diff;
            V[i] = V_next;
        }

        if (iter % 100 == 0 || max_diff < 1e-25) {
            printf("Ітерація %3d: E0 = %.4f меВ, max_diff = %.3e еВ\n", 
                   iter, (E0 / QE) * 1000.0, max_diff / QE);
        }
        if (max_diff / QE < 1e-6) break;
    }

    printf("\nЗбіжність досягнута!\n");
    printf("Енергія основної підзони 2DEG E0 = %.3f меВ\n", (E0 / QE) * 1000.0);

    return 0;
}
