#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

// Структура опису технічних параметрів резистора
typedef struct {
    double nominal_ohms; // номінальний опір, Ом
    double tol_percent;  // початковий допуск, % (наприклад, 1.0 для 1%)
    double tcr_ppm;      // температурний коефіцієнт, ppm/°C (наприклад, 50.0)
} ResistorSpec;

// Результати розрахунку та статистичного моделювання
typedef struct {
    double v_nominal;      // теоретична напруга за номіналом, В
    double v_min_wca;      // нижня межа найгіршого випадку WCA, В
    double v_max_wca;      // верхня межа найгіршого випадку WCA, В
    double v_mean_mc;      // середнє арифметичне Монте-Карло, В
    double v_std_mc;       // середньоквадратичне відхилення сигма, В
    double yield_percent;  // відсоток плат, що вклалися в допуск, %
} AnalysisResult;

// Генератор нормального розподілу Гауса (перетворення Бокса — Мюллера)
static double random_gaussian(double mean, double std_dev) {
    double u1 = ((double)rand() + 1.0) / ((double)RAND_MAX + 2.0);
    double u2 = ((double)rand() + 1.0) / ((double)RAND_MAX + 2.0);
    double z0 = sqrt(-2.0 * log(u1)) * cos(2.0 * M_PI * u2);
    return mean + z0 * std_dev;
}

// Функція передачі резистивного дільника V_out = V_in * R2 / (R1 + R2)
static double divider_output(double v_in, double r1, double r2) {
    return v_in * r2 / (r1 + r2);
}

AnalysisResult analyze_divider(double v_in, ResistorSpec r1, ResistorSpec r2,
                              double delta_temp_c, double v_target_min, double v_target_max,
                              int mc_samples) {
    AnalysisResult res;
    res.v_nominal = divider_output(v_in, r1.nominal_ohms, r2.nominal_ohms);

    // 1. Повний максимальний розкид кожного плеча (допуск виготовлення + температурний дрейф)
    double r1_drift_pct = r1.tol_percent + (r1.tcr_ppm * delta_temp_c * 1e-4);
    double r2_drift_pct = r2.tol_percent + (r2.tcr_ppm * delta_temp_c * 1e-4);

    double r1_min = r1.nominal_ohms * (1.0 - r1_drift_pct * 0.01);
    double r1_max = r1.nominal_ohms * (1.0 + r1_drift_pct * 0.01);
    double r2_min = r2.nominal_ohms * (1.0 - r2_drift_pct * 0.01);
    double r2_max = r2.nominal_ohms * (1.0 + r2_drift_pct * 0.01);

    // Найгірший детермінований випадок (протифазні екстремуми)
    res.v_min_wca = divider_output(v_in, r1_max, r2_min);
    res.v_max_wca = divider_output(v_in, r1_min, r2_max);

    // 2. Статистична симуляція Монте-Карло (модель 3-сигма)
    double sigma_r1 = (r1.nominal_ohms * r1_drift_pct * 0.01) / 3.0;
    double sigma_r2 = (r2.nominal_ohms * r2_drift_pct * 0.01) / 3.0;

    double sum_v = 0.0;
    double sum_v_sq = 0.0;
    int passing_samples = 0;

    for (int i = 0; i < mc_samples; ++i) {
        double sim_r1 = random_gaussian(r1.nominal_ohms, sigma_r1);
        double sim_r2 = random_gaussian(r2.nominal_ohms, sigma_r2);
        double sim_v = divider_output(v_in, sim_r1, sim_r2);

        sum_v += sim_v;
        sum_v_sq += sim_v * sim_v;

        if (sim_v >= v_target_min && sim_v <= v_target_max) {
            passing_samples++;
        }
    }

    res.v_mean_mc = sum_v / (double)mc_samples;
    double variance = (sum_v_sq / (double)mc_samples) - (res.v_mean_mc * res.v_mean_mc);
    res.v_std_mc = (variance > 0.0) ? sqrt(variance) : 0.0;
    res.yield_percent = ((double)passing_samples / (double)mc_samples) * 100.0;

    return res;
}

int main(void) {
    srand(42); // фіксований сід для повторюваності вибірки

    double v_in = 5.0; // напруга живлення 5.0 В
    ResistorSpec r1 = {10000.0, 1.0, 50.0}; // верхнє плече 10 кОм ±1%, 50 ppm/°C
    ResistorSpec r2 = {10000.0, 1.0, 50.0}; // нижнє плече 10 кОм ±1%, 50 ppm/°C

    double delta_t = 50.0;      // нагрів на 50 °C вище калібрувальних 25 °C
    double v_min_spec = 2.475;  // нижня межа допуску схеми 2.5 В - 1% (2.475 В)
    double v_max_spec = 2.525;  // верхня межа допуску схеми 2.5 В + 1% (2.525 В)

    AnalysisResult res = analyze_divider(v_in, r1, r2, delta_t, v_min_spec, v_max_spec, 100000);

    printf("====================================================\n");
    printf("   РЕЗУЛЬТАТИ ЧИСЛОВОГО АНАЛІЗУ ДІЛЬНИКА НАПРУГИ    \n");
    printf("====================================================\n");
    printf("Номінальна напруга:     %.4f В\n", res.v_nominal);
    printf("Межі Worst-Case (WCA):  %.4f В ... %.4f В\n", res.v_min_wca, res.v_max_wca);
    printf("Монте-Карло сер. (Mean):%.4f В\n", res.v_mean_mc);
    printf("Відхилення сигма (Std): %.5f В (%.3f мВ)\n", res.v_std_mc, res.v_std_mc * 1000.0);
    printf("Вихід придатних (Yield):%.2f %%\n", res.yield_percent);
    printf("====================================================\n");

    return 0;
}
