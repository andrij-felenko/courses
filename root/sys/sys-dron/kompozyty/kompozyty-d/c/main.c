#include <stdio.h>
#include <stdbool.h>
#include <math.h>

#define PI 3.14159265358979323846
#define DEG2RAD (PI / 180.0)

/* Характеристики односпрямованого моношару */
typedef struct {
    double E1;      /* Па: поздовжній модуль пружності */
    double E2;      /* Па: поперечний модуль пружності */
    double G12;     /* Па: модуль зсуву */
    double nu12;    /* Коефіцієнт Пуассона */
    double Xt;      /* Па: міцність на розтяг вздовж волокна */
    double Xc;      /* Па: міцність на стиск вздовж волокна */
    double Yt;      /* Па: міцність на поперечний розтяг */
    double Yc;      /* Па: міцність на поперечний стиск */
    double S;       /* Па: міцність на зсув */
    double t;       /* м: товщина моношару */
} CompositePly;

/* Обчислення плоских напружень та коефіцієнта запасу за Цаєм-Ву */
double calculate_tsai_wu_margin(const CompositePly* ply, double sigma1, double sigma2, double tau12) {
    double F1 = (1.0 / ply->Xt) - (1.0 / ply->Xc);
    double F2 = (1.0 / ply->Yt) - (1.0 / ply->Yc);
    double F11 = 1.0 / (ply->Xt * ply->Xc);
    double F22 = 1.0 / (ply->Yt * ply->Yc);
    double F66 = 1.0 / (ply->S * ply->S);
    double F12 = -0.5 * sqrt(F11 * F22);

    /* Квадратне рівняння для коефіцієнта навантаження SF: A*SF^2 + B*SF - 1 = 0 */
    double A = F11 * sigma1 * sigma1 + F22 * sigma2 * sigma2 +
               F66 * tau12 * tau12 + 2.0 * F12 * sigma1 * sigma2;
    double B = F1 * sigma1 + F2 * sigma2;

    if (A <= 1e-20) return 100.0;
    double discr = B * B + 4.0 * A;
    if (discr < 0.0) return 0.0;

    return (-B + sqrt(discr)) / (2.0 * A);
}

/* Розрахунок ефективного модуля та прогину трубчастого променя */
bool evaluate_composite_tube(
    const CompositePly* mat,
    const double* angles_deg,
    int num_layers,
    double length_m,
    double outer_rad_m,
    double thrust_force_n,
    double* out_Ex_eff,
    double* out_deflection_mm,
    double* out_min_sf
) {
    if (!mat || !angles_deg || num_layers <= 0) return false;

    double nu21 = (mat->nu12 * mat->E2) / mat->E1;
    double denom = 1.0 - mat->nu12 * nu21;

    double Q11 = mat->E1 / denom;
    double Q12 = (mat->nu12 * mat->E2) / denom;
    double Q22 = mat->E2 / denom;
    double Q66 = mat->G12;

    double A11 = 0.0, A12 = 0.0, A22 = 0.0;
    double total_h = num_layers * mat->t;

    for (int k = 0; k < num_layers; ++k) {
        double rad = angles_deg[k] * DEG2RAD;
        double m = cos(rad), n = sin(rad);
        double m2 = m * m, n2 = n * n;
        double m4 = m2 * m2, n4 = n2 * n2, m2n2 = m2 * n2;

        double Qbar11 = Q11 * m4 + 2.0 * (Q12 + 2.0 * Q66) * m2n2 + Q22 * n4;
        double Qbar12 = (Q11 + Q22 - 4.0 * Q66) * m2n2 + Q12 * (m4 + n4);
        double Qbar22 = Q11 * n4 + 2.0 * (Q12 + 2.0 * Q66) * m2n2 + Q22 * m4;

        A11 += Qbar11 * mat->t;
        A12 += Qbar12 * mat->t;
        A22 += Qbar22 * mat->t;
    }

    double Ex_eff = (A11 * A22 - A12 * A12) / (total_h * A22);
    double inner_rad_m = outer_rad_m - total_h;
    double I_xx = (PI / 4.0) * (pow(outer_rad_m, 4.0) - pow(inner_rad_m, 4.0));

    /* Максимальний прогин консолі w = F * L^3 / (3 * E * I) */
    double w_max = (thrust_force_n * pow(length_m, 3.0)) / (3.0 * Ex_eff * I_xx);

    /* Максимальна поздовжня деформація від вигину */
    double M_bend = thrust_force_n * length_m;
    double eps_x_max = (M_bend * outer_rad_m) / (Ex_eff * I_xx);

    double min_sf = 1e9;
    for (int k = 0; k < num_layers; ++k) {
        double rad = angles_deg[k] * DEG2RAD;
        double m = cos(rad), n = sin(rad);

        double eps1 = eps_x_max * m * m;
        double eps2 = eps_x_max * n * n;
        double gamma12 = -2.0 * eps_x_max * m * n;

        double sigma1 = Q11 * eps1 + Q12 * eps2;
        double sigma2 = Q12 * eps1 + Q22 * eps2;
        double tau12  = Q66 * gamma12;

        double sf = calculate_tsai_wu_margin(mat, sigma1, sigma2, tau12);
        if (sf < min_sf) min_sf = sf;
    }

    *out_Ex_eff = Ex_eff;
    *out_deflection_mm = w_max * 1e3;
    *out_min_sf = min_sf;
    return true;
}

int main(void) {
    CompositePly t700 = {
        .E1 = 135.0e9, .E2 = 9.0e9, .G12 = 4.8e9, .nu12 = 0.30,
        .Xt = 2100.0e6, .Xc = 1200.0e6, .Yt = 50.0e6, .Yc = 180.0e6, .S = 75.0e6,
        .t = 0.125e-3
    };

    double layup[8] = {0.0, 45.0, -45.0, 90.0, 90.0, -45.0, 45.0, 0.0};
    double Ex, deflection, sf;

    if (evaluate_composite_tube(&t700, layup, 8, 0.35, 0.0125, 45.0, &Ex, &deflection, &sf)) {
        printf("Модуль Ex: %.2f ГПа, Прогин: %.3f мм, Запас міцності: %.2f\n",
               Ex / 1e9, deflection, sf);
    }
    return 0;
}
