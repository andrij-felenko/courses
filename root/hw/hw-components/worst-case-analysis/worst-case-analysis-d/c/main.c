#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

/* Генерація випадкового числа з нормальним розподілом Гауса (Box-Muller) */
static double rand_gaussian(double mean, double stddev) {
    double u1 = ((double)rand() + 1.0) / ((double)RAND_MAX + 2.0);
    double u2 = ((double)rand() + 1.0) / ((double)RAND_MAX + 2.0);
    double z0 = sqrt(-2.0 * log(u1)) * cos(2.0 * M_PI * u2);
    return mean + z0 * stddev;
}

typedef struct {
    const char *name;
    double nom;      /* Номінальне значення */
    double tol_pct;  /* Сукупний життєвий допуск у % (End-of-Life) */
} Component;

/* Функція розрахунку виходу підсилювача: Vout = Vin * (1 + R2 / R1) */
static double calc_amplifier_vout(double vin, double r1, double r2) {
    return vin * (1.0 + r2 / r1);
}

int main(void) {
    srand(12345); /* Фіксований seed для повторюваності інженерного тесту */

    Component vin_src = {"Vin", 1.000, 0.50};  /* 1.000 В +- 0.5% */
    Component r1_res  = {"R1",  10000.0, 3.00}; /* 10.0 кОм +- 3.0% */
    Component r2_res  = {"R2",  90000.0, 3.00}; /* 90.0 кОм +- 3.0% */

    double v_nom = calc_amplifier_vout(vin_src.nom, r1_res.nom, r2_res.nom);

    /* 1. Чутливості (Sensitivity) */
    double sens_vin = 1.0 + r2_res.nom / r1_res.nom;
    double sens_r2  = vin_src.nom / r1_res.nom;
    double sens_r1  = -vin_src.nom * r2_res.nom / (r1_res.nom * r1_res.nom);

    double s_rel_vin = (vin_src.nom / v_nom) * sens_vin;
    double s_rel_r2  = (r2_res.nom / v_nom) * sens_r2;
    double s_rel_r1  = (r1_res.nom / v_nom) * sens_r1;

    /* 2. Метод граничних значень (EVA Worst-Case) */
    double vin_min = vin_src.nom * (1.0 - vin_src.tol_pct / 100.0);
    double vin_max = vin_src.nom * (1.0 + vin_src.tol_pct / 100.0);
    double r1_min  = r1_res.nom * (1.0 - r1_res.tol_pct / 100.0);
    double r1_max  = r1_res.nom * (1.0 + r1_res.tol_pct / 100.0);
    double r2_min  = r2_res.nom * (1.0 - r2_res.tol_pct / 100.0);
    double r2_max  = r2_res.nom * (1.0 + r2_res.tol_pct / 100.0);

    /* Для Vout_min: беремо Vin_min, R2_min, R1_max */
    double v_eva_min = calc_amplifier_vout(vin_min, r1_max, r2_min);
    /* Для Vout_max: беремо Vin_max, R2_max, R1_min */
    double v_eva_max = calc_amplifier_vout(vin_max, r1_min, r2_max);

    /* 3. Метод Root-Sum-Square (RSS 3-Sigma) */
    double var_sum = (s_rel_vin * vin_src.tol_pct) * (s_rel_vin * vin_src.tol_pct) +
                     (s_rel_r1  * r1_res.tol_pct)  * (s_rel_r1  * r1_res.tol_pct) +
                     (s_rel_r2  * r2_res.tol_pct)  * (s_rel_r2  * r2_res.tol_pct);
    double tol_rss_pct = sqrt(var_sum);
    double v_rss_min = v_nom * (1.0 - tol_rss_pct / 100.0);
    double v_rss_max = v_nom * (1.0 + tol_rss_pct / 100.0);

    /* 4. Симуляція Монте-Карло (100 000 прогонів) */
    const int NUM_RUNS = 100000;
    double vin_std = (vin_src.nom * (vin_src.tol_pct / 100.0)) / 3.0;
    double r1_std  = (r1_res.nom * (r1_res.tol_pct / 100.0)) / 3.0;
    double r2_std  = (r2_res.nom * (r2_res.tol_pct / 100.0)) / 3.0;

    double sum_v = 0.0, sum_sq_v = 0.0;
    double mc_min = 1e9, mc_max = -1e9;
    int fails_spec = 0;
    double spec_low = 9.60, spec_high = 10.40; /* Специфікація: 10.0 В +- 4.0% */

    for (int i = 0; i < NUM_RUNS; i++) {
        double v_i  = rand_gaussian(vin_src.nom, vin_std);
        double r1_i = rand_gaussian(r1_res.nom, r1_std);
        double r2_i = rand_gaussian(r2_res.nom, r2_std);

        double out = calc_amplifier_vout(v_i, r1_i, r2_i);
        sum_v += out;
        sum_sq_v += out * out;

        if (out < mc_min) mc_min = out;
        if (out > mc_max) mc_max = out;
        if (out < spec_low || out > spec_high) fails_spec++;
    }

    double mc_mean = sum_v / NUM_RUNS;
    double mc_stddev = sqrt((sum_sq_v / NUM_RUNS) - (mc_mean * mc_mean));
    double yield_pct = 100.0 * (1.0 - ((double)fails_spec / NUM_RUNS));

    printf("=== РЕЗУЛЬТАТИ АНАЛІЗУ НАЙГІРШОГО ВИПАДКУ (WCCA) ===\n");
    printf("Номінальний вихід Vout: %.4f В\n\n", v_nom);

    printf("1. Аналіз чутливості:\n");
    printf("   S_rel(Vin) = %+.4f (1%% дрейфу Vin змінює Vout на %+.2f%%)\n", s_rel_vin, s_rel_vin);
    printf("   S_rel(R1)  = %+.4f (1%% дрейфу R1  змінює Vout на %+.2f%%)\n", s_rel_r1, s_rel_r1);
    printf("   S_rel(R2)  = %+.4f (1%% дрейфу R2  змінює Vout на %+.2f%%)\n\n", s_rel_r2, s_rel_r2);

    printf("2. Метод граничних значень (EVA 100%% Worst-Case):\n");
    printf("   Vout_min = %.4f В (%+.2f%%)\n", v_eva_min, 100.0 * (v_eva_min - v_nom) / v_nom);
    printf("   Vout_max = %.4f В (%+.2f%%)\n", v_eva_max, 100.0 * (v_eva_max - v_nom) / v_nom);
    printf("   Сумарне вікно розкиду EVA: %.4f В\n\n", v_eva_max - v_eva_min);

    printf("3. Метод Root-Sum-Square (RSS 3-Sigma 99.73%%):\n");
    printf("   Статистичний допуск: +-%.2f%%\n", tol_rss_pct);
    printf("   Vout_min (3-Sigma) = %.4f В\n", v_rss_min);
    printf("   Vout_max (3-Sigma) = %.4f В\n\n", v_rss_max);

    printf("4. Моделювання Монте-Карло (%d ітерацій):\n", NUM_RUNS);
    printf("   Середнє значення mu:   %.4f В\n", mc_mean);
    printf("   Стандартне відхилення: %.4f В\n", mc_stddev);
    printf("   Діапазон вибірки:      [%.4f В ... %.4f В]\n", mc_min, mc_max);
    printf("   Вихід придатних (Yield): %.3f%% (Брак: %d PPM)\n",
           yield_pct, (int)((double)fails_spec / NUM_RUNS * 1000000.0));

    return 0;
}
