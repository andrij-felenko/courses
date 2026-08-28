/* electrostatic_sim.c - Чисельне моделювання індукції на заземленій площині (C) */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

/* Електрична стала ε₀ (Ф/м) */
#define EPSILON_0 8.8541878128e-12

/* Структура результатів моделювання */
typedef struct {
    double analytical_q_coulombs;
    double numerical_q_coulombs;
    double relative_error_percent;
    double attraction_force_newtons;
} sim_result_t;

/* Обчислення поверхневої густини заряду sigma(r) у Кл/м² */
double surface_charge_density(double q, double d, double r) {
    double denom = pow(r * r + d * d, 1.5);
    return -(q * d) / (2.0 * M_PI * denom);
}

/* Чисельне інтегрування наведеного заряду методом трапецій */
double integrate_induced_charge(double q, double d, double r_max, size_t steps) {
    if (steps == 0 || r_max <= 0.0) return 0.0;

    double dr = r_max / (double)steps;
    double total_q = 0.0;

    for (size_t i = 0; i < steps; i++) {
        double r1 = (double)i * dr;
        double r2 = (double)(i + 1) * dr;
        double sigma1 = surface_charge_density(q, d, r1);
        double sigma2 = surface_charge_density(q, d, r2);

        /* Інтегральний елемент кільця dQ = 2*pi*r*sigma(r)*dr */
        double dq1 = 2.0 * M_PI * r1 * sigma1;
        double dq2 = 2.0 * M_PI * r2 * sigma2;
        total_q += 0.5 * (dq1 + dq2) * dr;
    }

    return total_q;
}

/* Сила притягання точкового заряду до площини */
double calculate_attraction_force(double q, double d) {
    double k = 1.0 / (4.0 * M_PI * EPSILON_0);
    return k * (q * q) / (4.0 * d * d);
}

/* Запуск повного циклу моделювання */
sim_result_t run_simulation(double q, double d, double r_max, size_t steps) {
    sim_result_t res;
    res.analytical_q_coulombs = -q;
    res.numerical_q_coulombs = integrate_induced_charge(q, d, r_max, steps);
    res.relative_error_percent = fabs((res.numerical_q_coulombs - res.analytical_q_coulombs) / q) * 100.0;
    res.attraction_force_newtons = calculate_attraction_force(q, d);
    return res;
}

int main(void) {
    double q = 1.0e-6;      /* 1 мкКл (10⁻⁶ Кл) */
    double d = 0.05;        /* Відстань d = 5 см (0.05 м) */
    double r_max = 2.0;     /* Радіус інтегрування 2.0 м */
    size_t steps = 50000;

    printf("====================================================\n");
    printf("  Моделювання індукції: Точковий заряд біля площини  \n");
    printf("====================================================\n");
    printf("Заряд q = %.2e Кл, Відстань d = %.3f м\n\n", q, d);

    printf("Табулювання густини σ(r) біля осі симетрії:\n");
    printf("  r (м)       σ(r) (Кл/м²)\n");
    printf("  -------------------------\n");
    for (double r = 0.0; r <= 0.20; r += 0.04) {
        printf("  %.2f        %.5e\n", r, surface_charge_density(q, d, r));
    }

    sim_result_t res = run_simulation(q, d, r_max, steps);

    printf("\nРезультати чисельного інтегрування:\n");
    printf("  Теоретичний наведений заряд:  %.6e Кл\n", res.analytical_q_coulombs);
    printf("  Чисельно обчислений заряд:    %.6e Кл\n", res.numerical_q_coulombs);
    printf("  Відносна похибка обчислення:  %.4f %%\n", res.relative_error_percent);
    printf("  Сила притягання до площини:   %.6e Н\n", res.attraction_force_newtons);

    return 0;
}
