#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define C_VACUUM 299792458.0 /* Швидкість світла у вакуумі (м/с) */

/* Структура каталожного скла за Зельмейєром */
typedef struct {
    const char* name;
    double B1, B2, B3; /* Коефіцієнти B_i */
    double C1, C2, C3; /* Резонансні квадрати C_i (мкм²) */
} SellmeierGlassC;

/* Обчислення показника заломлення n(lambda) */
double glass_n(const SellmeierGlassC* g, double lambda_um) {
    double l2 = lambda_um * lambda_um;
    double n2 = 1.0 + (g->B1 * l2) / (l2 - g->C1)
                    + (g->B2 * l2) / (l2 - g->C2)
                    + (g->B3 * l2) / (l2 - g->C3);
    return sqrt(n2);
}

/* Перша похідна dn/dlambda за методом центральних різниць */
double glass_dn_dlambda(const SellmeierGlassC* g, double lambda_um) {
    double h = 0.0001; /* крок 0.1 нм */
    double n_plus  = glass_n(g, lambda_um + h);
    double n_minus = glass_n(g, lambda_um - h);
    return (n_plus - n_minus) / (2.0 * h);
}

/* Друга похідна d^2n / dlambda^2 */
double glass_d2n_dlambda2(const SellmeierGlassC* g, double lambda_um) {
    double h = 0.0001;
    double n_plus  = glass_n(g, lambda_um + h);
    double n_zero  = glass_n(g, lambda_um);
    double n_minus = glass_n(g, lambda_um - h);
    return (n_plus - 2.0 * n_zero + n_minus) / (h * h);
}

/* Обчислення групового показника n_g */
double glass_group_index(const SellmeierGlassC* g, double lambda_um) {
    double n = glass_n(g, lambda_um);
    double dn_dl = glass_dn_dlambda(g, lambda_um);
    return n - lambda_um * dn_dl;
}

/* Обчислення числа Аббе V_d = (n_d - 1) / (n_F - n_C) */
double glass_abbe_number(const SellmeierGlassC* g) {
    double n_d = glass_n(g, 0.587562); /* 587.56 нм (гелій d) */
    double n_F = glass_n(g, 0.486133); /* 486.13 нм (водень F) */
    double n_C = glass_n(g, 0.656273); /* 656.27 нм (водень C) */
    return (n_d - 1.0) / (n_F - n_C);
}

/* Обчислення матеріальної дисперсії D (пс / (нм * км)) */
double glass_material_dispersion(const SellmeierGlassC* g, double lambda_um) {
    double d2n = glass_d2n_dlambda2(g, lambda_um);
    double lambda_m = lambda_um * 1e-6;
    double d2n_m2 = d2n * 1e12;
    double D_s_m2 = -(lambda_m / C_VACUUM) * d2n_m2;
    return D_s_m2 * 1e6;
}

int main(void) {
    SellmeierGlassC bk7 = {
        "N-BK7",
        1.03961212, 0.231792344, 1.01046945,
        0.00600069867, 0.0200179144, 103.560653
    };

    double lambda = 0.587562; /* 587.56 нм */
    double n = glass_n(&bk7, lambda);
    double dn_dl = glass_dn_dlambda(&bk7, lambda);
    double n_g = glass_group_index(&bk7, lambda);
    double v_p = C_VACUUM / n;
    double v_g = C_VACUUM / n_g;
    double v_d = glass_abbe_number(&bk7);
    double D_mat = glass_material_dispersion(&bk7, lambda);

    printf("--- Дисперсійний паспорт матеріалу %s ---\n", bk7.name);
    printf("Довжина хвилі: %.6f мкм\n", lambda);
    printf("Показник заломлення n: %.6f\n", n);
    printf("Перша похідна dn/dlambda: %.6f 1/мкм\n", dn_dl);
    printf("Груповий показник n_g: %.6f\n", n_g);
    printf("Фазова швидкість v_p: %.2f км/с\n", v_p / 1000.0);
    printf("Групова швидкість v_g: %.2f км/с\n", v_g / 1000.0);
    printf("Число Аббе V_d: %.2f\n", v_d);
    printf("Матеріальна дисперсія D: %.2f пс/(нм*км)\n", D_mat);

    return 0;
}
