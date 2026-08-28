#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

/* Структура вхідних даних */
typedef struct {
    double M1;        /* Вхідне число Маха (M1 > 1.0) */
    double delta_deg; /* Кут повороту стінки в градусах */
    double gamma;     /* Показник адіабати (наприклад, 1.4 для повітря) */
} pm_input_t;

/* Структура результатів розрахунку */
typedef struct {
    double M2;           /* Вихідне число Маха */
    double nu1_deg;      /* Вхідна функція Прандтля — Майєра (град) */
    double nu2_deg;      /* Вихідна функція Прандтля — Майєра (град) */
    double mu1_deg;      /* Вхідний кут Маха (град) */
    double mu2_deg;      /* Вихідний кут Маха (град) */
    double p_ratio;      /* Відношення статичних тисків p2 / p1 */
    double T_ratio;      /* Відношення статичних температур T2 / T1 */
    double rho_ratio;    /* Відношення густин rho2 / rho1 */
    int is_valid;        /* Прапорець успішності (1 - успіх, 0 - помилка) */
} pm_output_t;

/* Обчислення прямої функції Прандтля — Майєра в радіанах */
double pm_nu_rad(double M, double gamma) {
    if (M <= 1.0) return 0.0;
    double g_factor = sqrt((gamma - 1.0) / (gamma + 1.0));
    double term1 = (1.0 / g_factor) * atan(g_factor * sqrt(M * M - 1.0));
    double term2 = atan(sqrt(M * M - 1.0));
    return term1 - term2;
}

/* Обчислення кута Маха в радіанах */
double pm_mu_rad(double M) {
    if (M <= 1.0) return M_PI / 2.0;
    return asin(1.0 / M);
}

/* Розв'язання оберненої задачі методом Ньютона — Рафсона */
double pm_inverse_nu(double nu_target_rad, double gamma) {
    double M = 1.5 + nu_target_rad;
    const double eps = 1e-12;
    const int max_iter = 100;

    for (int i = 0; i < max_iter; i++) {
        if (M < 1.000001) M = 1.000001;
        double f = pm_nu_rad(M, gamma) - nu_target_rad;
        if (fabs(f) < eps) break;

        double df_dM = sqrt(M * M - 1.0) / (M * (1.0 + 0.5 * (gamma - 1.0) * M * M));
        M = M - f / df_dM;
    }
    return M;
}

/* Головна функція розрахунку течії Прандтля — Майєра */
int pm_solve(const pm_input_t* in, pm_output_t* out) {
    if (!in || !out) return 0;
    if (in->M1 <= 1.0 || in->gamma <= 1.0 || in->delta_deg < 0.0) {
        out->is_valid = 0;
        return 0;
    }

    double delta_rad = in->delta_deg * (M_PI / 180.0);
    double nu1_rad = pm_nu_rad(in->M1, in->gamma);
    
    double g_factor = sqrt((in->gamma - 1.0) / (in->gamma + 1.0));
    double nu_max_rad = (M_PI / 2.0) * ((1.0 / g_factor) - 1.0);
    
    double nu2_rad = nu1_rad + delta_rad;
    if (nu2_rad >= nu_max_rad) {
        out->is_valid = 0;
        return 0;
    }

    out->M2 = pm_inverse_nu(nu2_rad, in->gamma);
    out->nu1_deg = nu1_rad * (180.0 / M_PI);
    out->nu2_deg = nu2_rad * (180.0 / M_PI);
    out->mu1_deg = pm_mu_rad(in->M1) * (180.0 / M_PI);
    out->mu2_deg = pm_mu_rad(out->M2) * (180.0 / M_PI);

    double tau1 = 1.0 + 0.5 * (in->gamma - 1.0) * in->M1 * in->M1;
    double tau2 = 1.0 + 0.5 * (in->gamma - 1.0) * out->M2 * out->M2;

    out->T_ratio = tau1 / tau2;
    out->p_ratio = pow(tau1 / tau2, in->gamma / (in->gamma - 1.0));
    out->rho_ratio = pow(tau1 / tau2, 1.0 / (in->gamma - 1.0));
    out->is_valid = 1;

    return 1;
}

int main(void) {
    pm_input_t input = {
        .M1 = 1.50,
        .delta_deg = 20.0,
        .gamma = 1.40
    };
    pm_output_t output;

    printf("=== Розрахунок течії Прандтля — Майєра (C) ===\n");
    printf("Вхідні дані: M1 = %.2f, Δθ = %.1f deg, gamma = %.2f\n\n",
           input.M1, input.delta_deg, input.gamma);

    if (pm_solve(&input, &output)) {
        printf("Результати:\n");
        printf("• Вихідне число Маха M2:       %.4f\n", output.M2);
        printf("• Функція ν(M1) -> ν(M2):     %.2f deg -> %.2f deg\n", output.nu1_deg, output.nu2_deg);
        printf("• Кути Маха μ(M1) -> μ(M2):    %.2f deg -> %.2f deg\n", output.mu1_deg, output.mu2_deg);
        printf("• Відношення тисків p2/p1:     %.4f (спад на %.1f%%)\n", output.p_ratio, (1.0 - output.p_ratio) * 100.0);
        printf("• Відношення температур T2/T1: %.4f (спад на %.1f%%)\n", output.T_ratio, (1.0 - output.T_ratio) * 100.0);
        printf("• Відношення густин ρ2/ρ1:    %.4f (спад на %.1f%%)\n", output.rho_ratio, (1.0 - output.rho_ratio) * 100.0);
    } else {
        printf("Помилка: Неприпустимі вхідні параметри або перевищено вакуумну межу.\n");
    }

    return 0;
}
