#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define KB_EV 8.617333262145e-5

typedef struct {
    double t_ox_nm;
    double a_test_cm2;
    double a_chip_cm2;
} TDDBConfig;

typedef struct {
    double beta;
    double eta;
} WeibullFit;

typedef struct {
    double voltage;
    double eta;
} StressPoint;

/* Функція порівняння для швидкого сортування qsort */
static int compare_doubles(const void *a, const void *b) {
    double da = *(const double *)a;
    double db = *(const double *)b;
    return (da > db) - (da < db);
}

/* Оцінка параметрів Вейбула методом найменших квадратів */
WeibullFit fit_weibull(double *samples, size_t n) {
    WeibullFit result;
    qsort(samples, n, sizeof(double), compare_doubles);

    double sum_x = 0.0, sum_y = 0.0, sum_xx = 0.0, sum_xy = 0.0;
    for (size_t i = 1; i <= n; ++i) {
        double f = ((double)i - 0.3) / ((double)n + 0.4);
        double x = log(samples[i - 1]);
        double y = log(-log(1.0 - f));
        sum_x += x;
        sum_y += y;
        sum_xx += x * x;
        sum_xy += x * y;
    }

    double dn = (double)n;
    double slope = (dn * sum_xy - sum_x * sum_y) / (dn * sum_xx - sum_x * sum_x);
    double intercept = (sum_y - slope * sum_x) / dn;

    result.beta = slope;
    result.eta = exp(-intercept / slope);
    return result;
}

/* Оцінка показника n_v степеневої моделі напруги */
double fit_power_law_voltage(const StressPoint *points, size_t n) {
    double sum_x = 0.0, sum_y = 0.0, sum_xx = 0.0, sum_xy = 0.0;
    for (size_t i = 0; i < n; ++i) {
        double x = log(points[i].voltage);
        double y = log(points[i].eta);
        sum_x += x;
        sum_y += y;
        sum_xx += x * x;
        sum_xy += x * y;
    }
    double dn = (double)n;
    double slope = (dn * sum_xy - sum_x * sum_y) / (dn * sum_xx - sum_x * sum_x);
    return -slope;
}

/* Розрахунок коефіцієнта прискорення AF */
double calculate_af(double v_stress, double v_op, double n_v,
                    double t_stress_c, double t_op_c, double ea_ev) {
    double af_v = pow(v_stress / v_op, n_v);
    double t_stress_k = t_stress_c + 273.15;
    double t_op_k = t_op_c + 273.15;
    double delta_inv_t = (1.0 / t_op_k) - (1.0 / t_stress_k);
    double af_t = exp((ea_ev / KB_EV) * delta_inv_t);
    return af_v * af_t;
}

/* Екстраполяція ресурсу для чіпа */
double extrapolate_chip_years(const TDDBConfig *cfg, double eta_stress,
                              double af_total, double beta, double target_f) {
    double eta_op_test = eta_stress * af_total;
    double area_scale = pow(cfg->a_test_cm2 / cfg->a_chip_cm2, 1.0 / beta);
    double eta_op_chip = eta_op_test * area_scale;
    double w_target = -log(1.0 - target_f);
    double t_sec = eta_op_chip * pow(w_target, 1.0 / beta);
    return t_sec / (365.25 * 24.0 * 3600.0);
}

int main(void) {
    TDDBConfig cfg = { .t_ox_nm = 1.4, .a_test_cm2 = 1e-6, .a_chip_cm2 = 0.05 };
    double samples[] = {
        450.2, 780.5, 920.1, 1105.4, 1340.8, 1560.2, 1780.9, 1950.0,
        2240.3, 2510.6, 2890.4, 3210.1, 3650.8, 4120.5, 4890.2
    };
    size_t n_samples = sizeof(samples) / sizeof(samples[0]);

    WeibullFit wf = fit_weibull(samples, n_samples);
    printf("Оцінений нахил Вейбула beta: %.2f\n", wf.beta);
    printf("Характеристичний час стресу eta: %.1f с\n", wf.eta);

    StressPoint stress_pts[] = {
        { 2.8, 450.0 },
        { 2.6, wf.eta },
        { 2.4, 15400.0 }
    };
    double n_v = fit_power_law_voltage(stress_pts, 3);
    printf("Показник напругового прискорення n_v: %.1f\n", n_v);

    double af = calculate_af(2.6, 0.85, n_v, 125.0, 85.0, 0.75);
    printf("Загальний коефіцієнт прискорення AF: %.2e\n", af);

    double years_100ppm = extrapolate_chip_years(&cfg, wf.eta, af, wf.beta, 0.0001);
    printf("Термін служби чіпа до 100 ppm браку: %.2e років\n", years_100ppm);

    return 0;
}
