#include <stdio.h>
#include <math.h>
#include <complex.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef struct {
    double complex r_s;  /* Комплексний амплітудний коефіцієнт відбиття s */
    double complex r_p;  /* Комплексний амплітудний коефіцієнт відбиття p */
    double complex t_s;  /* Комплексний амплітудний коефіцієнт заломлення s */
    double complex t_p;  /* Комплексний амплітудний коефіцієнт заломлення p */
    double R_s;          /* Енергетична відбивність s-поляризації */
    double R_p;          /* Енергетична відбивність p-поляризації */
    double T_s;          /* Енергетичне пропускання s-поляризації */
    double T_p;          /* Енергетичне пропускання p-поляризації */
    double R_avg;        /* Середня відбивність неполяризованого світла */
    double phase_s_deg;  /* Зсув фази s-хвилі при відбитті (в градусах) */
    double phase_p_deg;  /* Зсув фази p-хвилі при відбитті (в градусах) */
} fresnel_result_t;

fresnel_result_t calc_fresnel(double complex n1, double complex n2, double theta1_deg) {
    fresnel_result_t res;
    double theta1_rad = theta1_deg * M_PI / 180.0;
    
    double complex cos_t1 = cos(theta1_rad);
    double complex sin_t1 = sin(theta1_rad);

    /* Комплексний закон Снелла */
    double complex sin_t2 = (n1 / n2) * sin_t1;
    double complex cos_t2 = csqrt(1.0 - sin_t2 * sin_t2);

    /* Захист від вибору не тієї гілки квадратного кореня */
    if (creal(cos_t2) < 0.0) {
        cos_t2 = -cos_t2;
    }

    /* Амплітудні коефіцієнти Френеля */
    res.r_s = (n1 * cos_t1 - n2 * cos_t2) / (n1 * cos_t1 + n2 * cos_t2);
    res.t_s = (2.0 * n1 * cos_t1) / (n1 * cos_t1 + n2 * cos_t2);

    res.r_p = (n2 * cos_t1 - n1 * cos_t2) / (n2 * cos_t1 + n1 * cos_t2);
    res.t_p = (2.0 * n1 * cos_t1) / (n2 * cos_t1 + n1 * cos_t2);

    /* Енергетична відбивність R = |r|^2 */
    res.R_s = cabs(res.r_s) * cabs(res.r_s);
    res.R_p = cabs(res.r_p) * cabs(res.r_p);
    res.R_avg = 0.5 * (res.R_s + res.R_p);

    /* Зсуви фаз при відбитті */
    res.phase_s_deg = carg(res.r_s) * 180.0 / M_PI;
    res.phase_p_deg = carg(res.r_p) * 180.0 / M_PI;

    /* Дійсний потік енергії для пропускання T */
    double complex factor = (n2 * cos_t2) / (n1 * cos_t1);
    double real_factor = creal(factor);
    if (real_factor < 0.0) real_factor = 0.0;

    res.T_s = real_factor * (cabs(res.t_s) * cabs(res.t_s));
    res.T_p = real_factor * (cabs(res.t_p) * cabs(res.t_p));

    return res;
}

int main(void) {
    /* Приклад 1: Повітря (n=1.0) -> Скло (n=1.5) під кутом 45 градусів */
    double complex n_air = 1.0 + 0.0 * I;
    double complex n_glass = 1.5 + 0.0 * I;
    fresnel_result_t res_glass = calc_fresnel(n_air, n_glass, 45.0);

    printf("=== Межа Повітря -> Скло (theta1 = 45 deg) ===\n");
    printf("R_s: %.4f (%.2f%%)\n", res_glass.R_s, res_glass.R_s * 100.0);
    printf("R_p: %.4f (%.2f%%)\n", res_glass.R_p, res_glass.R_p * 100.0);
    printf("R_avg: %.4f (%.2f%%)\n", res_glass.R_avg, res_glass.R_avg * 100.0);
    printf("T_s: %.4f, T_p: %.4f\n", res_glass.T_s, res_glass.T_p);

    /* Приклад 2: Золото при довжині хвилі 633 нм (n = 0.18 + 3.43i) */
    double complex n_gold = 0.18 + 3.43 * I;
    fresnel_result_t res_gold = calc_fresnel(n_air, n_gold, 0.0);

    printf("\n=== Межа Повітря -> Золото при нормальному падінні (0 deg) ===\n");
    printf("R_s = R_p: %.4f (%.2f%%)\n", res_gold.R_s, res_gold.R_s * 100.0);

    return 0;
}
