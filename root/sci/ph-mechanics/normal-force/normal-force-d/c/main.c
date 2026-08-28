#include <stdio.h>
#include <math.h>
#include <stdbool.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef struct {
    double R1, R2;         /* Радіуси кривини тіл, м (для площини R2 = 1e20) */
    double E1, E2;         /* Модулі пружності Юнга, Па */
    double nu1, nu2;       /* Коефіцієнти Пуассона */
    double yield_strength; /* Границя текучості матеріалу, Па */
} ContactMaterial;

typedef struct {
    double a;              /* Радіус кругової плями контакту, м */
    double delta;          /* Пружне нормальне зближення центрів, м */
    double p0;             /* Максимальний контактний тиск у центрі, Па */
    double p_mean;         /* Середній контактний тиск, Па */
    double tau_max;        /* Максимальне підповерхневе зсувне напруження, Па */
    double z_crit;         /* Глибина залягання піка зсуву, м */
    double sigma_tensile;  /* Радіальне напруження розтягу на краю плями, Па */
    double safety_factor;  /* Коефіцієнт запасу за критерієм Треска */
    bool is_elastic;       /* Чи залишається контакт у пружній зоні */
} HertzSphereResult;

/* Обчислення приведеного модуля пружності E* */
static inline double hertz_reduced_modulus(double E1, double nu1, double E2, double nu2) {
    double inv_E = (1.0 - nu1 * nu1) / E1 + (1.0 - nu2 * nu2) / E2;
    return 1.0 / inv_E;
}

/* Обчислення еквівалентного радіуса кривини R */
static inline double hertz_reduced_radius(double R1, double R2) {
    return (R1 * R2) / (R1 + R2);
}

/* Повний розрахунок пружного контакту двох сфер за Герцом */
bool hertz_sphere_contact(const ContactMaterial *mat, double normal_force, HertzSphereResult *res) {
    if (!mat || !res || normal_force <= 0.0 || mat->R1 <= 0.0 || mat->R2 <= 0.0) {
        return false;
    }

    double R = hertz_reduced_radius(mat->R1, mat->R2);
    double E_star = hertz_reduced_modulus(mat->E1, mat->nu1, mat->E2, mat->nu2);

    /* 1. Радіус плями контакту a = ( (3 * N * R) / (4 * E*) )^(1/3) */
    res->a = cbrt((3.0 * normal_force * R) / (4.0 * E_star));

    /* 2. Пружне нормальне зближення delta = a^2 / R */
    res->delta = (res->a * res->a) / R;

    /* 3. Піковий та середній контактний тиск */
    res->p0 = (3.0 * normal_force) / (2.0 * M_PI * res->a * res->a);
    res->p_mean = (2.0 / 3.0) * res->p0;

    /* 4. Підповерхневі екстремальні зсувні напруження (Tresca) */
    res->tau_max = 0.3105 * res->p0;
    res->z_crit = 0.481 * res->a;

    /* 5. Радіальне напруження розтягу на контурі контакту r = a */
    res->sigma_tensile = res->p0 * (1.0 - 2.0 * mat->nu1) / 3.0;

    /* 6. Перевірка міцності за критерієм текучості Треска: 2 * tau_max <= sigma_y */
    double allowable_tau = 0.5 * mat->yield_strength;
    res->safety_factor = allowable_tau / res->tau_max;
    res->is_elastic = (res->safety_factor >= 1.0);

    return true;
}

int main(void) {
    /* Приклад: сталева кулька підшипника ШХ15 (R1 = 10 мм) на сталевій площині (R2 = 1e9) */
    ContactMaterial steel_bearing = {
        .R1 = 0.010,           /* 10 мм */
        .R2 = 1.0e9,           /* площина */
        .E1 = 210.0e9,         /* 210 ГПа */
        .E2 = 210.0e9,
        .nu1 = 0.30,
        .nu2 = 0.30,
        .yield_strength = 1800.0e6 /* 1800 МПа */
    };

    double N = 1500.0; /* Нормальне навантаження 1500 Н (~153 кг) */
    HertzSphereResult res;

    if (hertz_sphere_contact(&steel_bearing, N, &res)) {
        printf("=== Результати розрахунку нормального контакту Герца ===\n");
        printf("Нормальна сила N:              %.1f Н\n", N);
        printf("Радіус плями контакту a:       %.3f мм\n", res.a * 1e3);
        printf("Глибина зближення delta:       %.3f мкм\n", res.delta * 1e6);
        printf("Піковий контактний тиск p0:    %.1f МПа\n", res.p0 / 1e6);
        printf("Середній контактний тиск p_avg:%.1f МПа\n", res.p_mean / 1e6);
        printf("Макс. зсувне напруження tau:   %.1f МПа\n", res.tau_max / 1e6);
        printf("Глибина залягання піка z_crit: %.3f мм\n", res.z_crit * 1e3);
        printf("Крайовий розтяг sigma_r(a):    %.1f МПа\n", res.sigma_tensile / 1e6);
        printf("Коефіцієнт запасу міцності:    %.2f (%s)\n",
               res.safety_factor, res.is_elastic ? "ПРУЖНИЙ СТАН" : "ПЛАСТИЧНА ТЕКУЧІСТЬ");
    }

    return 0;
}
