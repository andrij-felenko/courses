#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define HERTZ_PI 3.14159265358979323846

/* Структура фізичних властивостей матеріалу */
typedef struct {
    double E;      /* Модуль пружності Юнга (Па) */
    double nu;     /* Коефіцієнт Пуассона (безрозмірний) */
} hertz_material_t;

/* Результати розрахунку сферичного контакту (точковий контакт) */
typedef struct {
    double R_star;   /* Зведений радіус кривини (м) */
    double E_star;   /* Зведений модуль пружності (Па) */
    double a;        /* Радіус плями контакту (м) */
    double delta;    /* Глибина втискання/зближення (м) */
    double p0;       /* Піковий контактний тиск (Па) */
    double p_mean;   /* Середній контактний тиск (Па) */
    double area;     /* Площа контакту (м²) */
    double z_peak;   /* Глибина піку зсувного напруження (м) */
    double tau_max;  /* Максимальне зсувне напруження (Па) */
} hertz_sphere_result_t;

/* Результати розрахунку циліндричного контакту (лінійний контакт) */
typedef struct {
    double R_star;   /* Зведений радіус кривини (м) */
    double E_star;   /* Зведений модуль пружності (Па) */
    double b;        /* Півширина контакту (м) */
    double delta;    /* Зближення поверхонь (м) */
    double p0;       /* Піковий контактний тиск (Па) */
    double p_mean;   /* Середній контактний тиск (Па) */
    double area;     /* Площа контакту (м²) */
} hertz_cylinder_result_t;

/* Точка профілю напружень по глибині z */
typedef struct {
    double z;          /* Глибина під поверхнею (м) */
    double z_over_a;   /* Відносна глибина z / a */
    double sigma_z;    /* Осьове стискальне напруження (Па) */
    double sigma_x;    /* Радіальне стискальне напруження (Па) */
    double tau_max;    /* Максимальне зсувне напруження (Па) */
} hertz_stress_point_t;

/* Розрахунок зведеного радіуса кривини: 1/R* = 1/R1 + 1/R2 */
double hertz_calc_r_star(double R1, double R2) {
    if (R1 <= 0.0 || R2 <= 0.0) return 0.0;
    return (R1 * R2) / (R1 + R2);
}

/* Розрахунок зведеного модуля пружності: 1/E* = (1-nu1^2)/E1 + (1-nu2^2)/E2 */
double hertz_calc_e_star(hertz_material_t mat1, hertz_material_t mat2) {
    if (mat1.E <= 0.0 || mat2.E <= 0.0) return 0.0;
    double inv_E1 = (1.0 - mat1.nu * mat1.nu) / mat1.E;
    double inv_E2 = (1.0 - mat2.nu * mat2.nu) / mat2.E;
    return 1.0 / (inv_E1 + inv_E2);
}

/* Солвер сферичного контакту (два тіла з радіусами R1, R2 під силою F) */
int hertz_solve_sphere(double F, double R1, double R2, 
                       hertz_material_t mat1, hertz_material_t mat2,
                       hertz_sphere_result_t *res) {
    if (!res || F <= 0.0) return -1;

    res->R_star = hertz_calc_r_star(R1, R2);
    res->E_star = hertz_calc_e_star(mat1, mat2);
    if (res->R_star <= 0.0 || res->E_star <= 0.0) return -2;

    /* a = ((3 * F * R*) / (4 * E*))^(1/3) */
    res->a = cbrt((3.0 * F * res->R_star) / (4.0 * res->E_star));

    /* delta = a^2 / R* */
    res->delta = (res->a * res->a) / res->R_star;

    /* p0 = (3 * F) / (2 * pi * a^2) */
    res->area = HERTZ_PI * res->a * res->a;
    res->p0 = (3.0 * F) / (2.0 * res->area);
    res->p_mean = F / res->area;

    /* Глибина піку та максимальний зсув для сталі (nu ≈ 0.3) */
    res->z_peak = 0.481 * res->a;
    res->tau_max = 0.310 * res->p0;

    return 0;
}

/* Солвер циліндричного контакту (циліндри довжиною L під силою F) */
int hertz_solve_cylinder(double F, double L, double R1, double R2,
                         hertz_material_t mat1, hertz_material_t mat2,
                         hertz_cylinder_result_t *res) {
    if (!res || F <= 0.0 || L <= 0.0) return -1;

    res->R_star = hertz_calc_r_star(R1, R2);
    res->E_star = hertz_calc_e_star(mat1, mat2);
    if (res->R_star <= 0.0 || res->E_star <= 0.0) return -2;

    /* b = sqrt((4 * F * R*) / (pi * L * E*)) */
    res->b = sqrt((4.0 * F * res->R_star) / (HERTZ_PI * L * res->E_star));

    /* delta для циліндра (наближення) */
    res->delta = (2.0 * F / (HERTZ_PI * L * res->E_star)) * (1.0 + log((HERTZ_PI * L * L * res->E_star) / (F * res->R_star)));

    /* p0 = sqrt((F * E*) / (pi * L * R*)) */
    res->p0 = sqrt((F * res->E_star) / (HERTZ_PI * L * res->R_star));
    res->area = 2.0 * res->b * L;
    res->p_mean = F / res->area;

    return 0;
}

/* Розрахунок профілю напружень вздовж осі z під центром контакту */
int hertz_calc_stress_profile(const hertz_sphere_result_t *sph, 
                              double z_max, int steps, 
                              hertz_stress_point_t *profile) {
    if (!sph || !profile || steps <= 0 || z_max <= 0.0) return -1;

    double nu = 0.3; /* Стандартне значення для сталі */
    double dz = z_max / steps;

    for (int i = 0; i <= steps; i++) {
        double z = i * dz;
        double za = (sph->a > 0.0) ? (z / sph->a) : 0.0;

        profile[i].z = z;
        profile[i].z_over_a = za;

        if (za < 1e-6) {
            profile[i].sigma_z = -sph->p0;
            profile[i].sigma_x = -sph->p0 * (0.5 + nu);
        } else {
            profile[i].sigma_z = -sph->p0 / (1.0 + za * za);
            profile[i].sigma_x = -sph->p0 * ((1.0 + nu) * (1.0 - za * atan(1.0 / za)) - 0.5 / (1.0 + za * za));
        }

        profile[i].tau_max = 0.5 * fabs(profile[i].sigma_z - profile[i].sigma_x);
    }

    return 0;
}

int main(void) {
    /* Сталь по сталі: E = 210 ГПа, nu = 0.3 */
    hertz_material_t steel = { .E = 210e9, .nu = 0.30 };

    /* Кулька радіусом 10 мм тисне на площину (R2 = 1e9 мм) силю F = 5000 Н */
    double F = 5000.0;
    double R1 = 0.010;   /* 10 мм */
    double R2 = 1.0e9;   /* Площина */

    hertz_sphere_result_t res;
    if (hertz_solve_sphere(F, R1, R2, steel, steel, &res) == 0) {
        printf("=== Розрахунок контакту сфери з площиною ===\n");
        printf("Сила F:                     %.1f Н\n", F);
        printf("Радіус плями контакту a:    %.4f мм\n", res.a * 1e3);
        printf("Глибина втискання delta:    %.4f мкм\n", res.delta * 1e6);
        printf("Піковий контактний тиск p0: %.2f МПа\n", res.p0 / 1e6);
        printf("Середній тиск p_сер:        %.2f МПа\n", res.p_mean / 1e6);
        printf("Глибина піку зсуву z_пік:   %.4f мм\n", res.z_peak * 1e3);
        printf("Максимальний зсув tau_max:  %.2f МПа\n", res.tau_max / 1e6);
    }

    /* Таблиця напружень по глибині z */
    int steps = 5;
    hertz_stress_point_t profile[6];
    if (hertz_calc_stress_profile(&res, 2.0 * res.a, steps, profile) == 0) {
        printf("\n--- Розподіл напружень по глибині z ---\n");
        printf(" z/a   |  z (мм) |  sigma_z (МПа) |  sigma_x (МПа) |  tau_max (МПа)\n");
        printf("-------+---------+----------------+----------------+----------------\n");
        for (int i = 0; i <= steps; i++) {
            printf(" %4.2f  |  %6.4f |    %10.2f  |    %10.2f  |    %10.2f\n",
                   profile[i].z_over_a,
                   profile[i].z * 1e3,
                   profile[i].sigma_z / 1e6,
                   profile[i].sigma_x / 1e6,
                   profile[i].tau_max / 1e6);
        }
    }

    return 0;
}
