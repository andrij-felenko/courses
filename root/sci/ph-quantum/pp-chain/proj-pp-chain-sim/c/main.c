/* C99 Implementation of PP-Chain Branching and Energy Solver */
#include <stdio.h>
#include <math.h>

typedef struct {
    double temp_k;        /* Температура плазми в Кельвінах */
    double density_gcm3;  /* Густина в г/см³ */
    double x_hyd;         /* Масова частка водню X (0..1) */
    double y_hel;         /* Масова частка гелію-4 Y (0..1) */
} StellarCoreConditions;

typedef struct {
    double branch_pp1;    /* Частка гілки pp-I (0..1) */
    double branch_pp2;    /* Частка гілки pp-II (0..1) */
    double branch_pp3;    /* Частка гілки pp-III (0..1) */
    double branch_hep;    /* Частка гілки pp-IV/hep (0..1) */
    double q_eff_mev;     /* Корисна енергія на ядро He-4 (МЕв) */
    double nu_loss_mev;   /* Втрати енергії нейтрино (МЕв) */
    double energy_gen_wkg;/* Питоме енерговиділення (Вт/кг) */
} PPChainResult;

PPChainResult solve_pp_chain(const StellarCoreConditions* cond) {
    PPChainResult res;
    double T6 = cond->temp_k / 1.0e6;
    double rho = cond->density_gcm3;
    double X = cond->x_hyd;
    double Y = cond->y_hel;

    /* Термодинамічні коефіцієнти реакцій (REACLIB parametrizations) */
    double T6_13 = cbrt(T6);
    double T6_23 = T6_13 * T6_13;

    /* 1. Швидкісні параметри r_ij */
    double r11 = 4.0e-15 * (1.0 / T6_23) * exp(-33.804 / T6_13);
    double r33 = 1.2e+04 * (1.0 / T6_23) * exp(-122.76 / T6_13);
    double r34 = 5.6e+05 * (1.0 / T6_23) * exp(-128.01 / T6_13);
    double r71 = 3.1e+05 * (1.0 / T6_23) * exp(-137.56 / T6_13);
    
    /* Електронне захоплення Be-7 */
    double mu_e = 2.0 / (1.0 + X);
    double lambda_7e = 1.34e-9 * (rho / mu_e) * (1.0 / sqrt(T6));

    /* 2. Конкурентні відношення гілкування */
    double ratio_34_33 = (r34 * Y) / (r33 * X + 1.0e-30);
    double f_be = ratio_34_33 / (1.0 + ratio_34_33);
    double f_pp1 = 1.0 - f_be;

    double ratio_71_7e = (r71 * X * rho) / (lambda_7e + 1.0e-30);
    double f_pp3 = f_be * (ratio_71_7e / (1.0 + ratio_71_7e));
    double f_pp2 = f_be - f_pp3;
    double f_hep = 2.0e-7; /* Завжди малий фіксований внесок */

    res.branch_pp1 = f_pp1;
    res.branch_pp2 = f_pp2;
    res.branch_pp3 = f_pp3;
    res.branch_hep = f_hep;

    /* 3. Енергетичні втрати нейтрино для кожної гілки */
    double q_nu = f_pp1 * 0.530 + f_pp2 * 1.127 + f_pp3 * 6.975;
    res.nu_loss_mev = q_nu;
    res.q_eff_mev = 26.731 - q_nu;

    /* 4. Питоме енерговиділення (ε_pp) у Вт/кг */
    double eps = 0.241 * rho * X * X * (1.0 / T6_23) * exp(-33.804 / T6_13);
    res.energy_gen_wkg = eps * 1.0e-4; /* Конвертація в Вт/кг */

    return res;
}

int main(void) {
    StellarCoreConditions sun_center = {
        .temp_k = 15.7e6,
        .density_gcm3 = 150.0,
        .x_hyd = 0.35,
        .y_hel = 0.63
    };

    PPChainResult res = solve_pp_chain(&sun_center);

    printf("=== МОДЕЛЮВАННЯ PP-ЛАНЦЮЖКА У ЦЕНТРІ СОНЦЯ (C99) ===\n");
    printf("Температура: %.2f МК, Густина: %.1f г/см³\n", sun_center.temp_k / 1e6, sun_center.density_gcm3);
    printf("Частка pp-I  гілки: %6.2f%%\n", res.branch_pp1 * 100.0);
    printf("Частка pp-II гілки: %6.2f%%\n", res.branch_pp2 * 100.0);
    printf("Частка pp-III гілки: %6.4f%%\n", res.branch_pp3 * 100.0);
    printf("Нейтринні втрати:   %6.3f МЕв на ядро He-4\n", res.nu_loss_mev);
    printf("Корисне Q_eff:       %6.3f МЕв\n", res.q_eff_mev);
    printf("Питоме виділення:   %.4e Вт/кг\n", res.energy_gen_wkg);

    return 0;
}
