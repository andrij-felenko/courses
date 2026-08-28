/* C: Модуль обчислення діелектричної проникності та первинної фільтрації */
#include <stdio.h>
#include <math.h>
#include <stdbool.h>
#include <string.h>

#define MEDIAN_WINDOW 5

typedef struct {
    double c0_farads;       /* Повітряна ємність датчика C₀ (наприклад 12.5 пФ) */
    double cp_farads;       /* Паразитна ємність C_p (наприклад 3.2 пФ) */
    double f0_hz;           /* Калібрувальна частота повітря f₀ (наприклад 500000 Гц) */
    double temp_coef_ppm;   /* Температурний коефіцієнт дрейфу */
} dielectric_calib_t;

typedef struct {
    double eps_real;        /* Дійсна частина ε' */
    double eps_imag;        /* Уявна частина ε'' */
    double loss_tangent;    /* tan δ */
    double capacity_pfd;    /* Виміряна ємність у пФ */
    bool is_valid;
} dielectric_result_t;

/* Медіанний фільтр для усунення імпульсних завад лічильника частоти */
static double apply_median_filter(double new_sample) {
    static double buffer[MEDIAN_WINDOW] = {0};
    static int idx = 0;
    buffer[idx] = new_sample;
    idx = (idx + 1) % MEDIAN_WINDOW;

    double sorted[MEDIAN_WINDOW];
    memcpy(sorted, buffer, sizeof(sorted));
    for (int i = 0; i < MEDIAN_WINDOW - 1; i++) {
        for (int j = i + 1; j < MEDIAN_WINDOW; j++) {
            if (sorted[i] > sorted[j]) {
                double tmp = sorted[i];
                sorted[i] = sorted[j];
                sorted[j] = tmp;
            }
        }
    }
    return sorted[MEDIAN_WINDOW / 2];
}

dielectric_result_t process_lc_measurement(const dielectric_calib_t* calib, 
                                           double raw_freq_hz, 
                                           double temp_celsius) {
    dielectric_result_t res;
    memset(&res, 0, sizeof(res));

    if (!calib || raw_freq_hz <= 10.0 || calib->f0_hz <= 10.0) {
        return res;
    }

    double filtered_freq = apply_median_filter(raw_freq_hz);

    /* Термокомпенсація калібрувальної частоти повітря */
    double temp_diff = temp_celsius - 20.0;
    double f0_compensated = calib->f0_hz * (1.0 + calib->temp_coef_ppm * 1e-6 * temp_diff);

    double ratio = f0_compensated / filtered_freq;
    double ratio_sq = ratio * ratio;

    double c_factor = 1.0 + (calib->cp_farads / calib->c0_farads);
    res.eps_real = 1.0 + (ratio_sq - 1.0) * c_factor;

    double total_cap = calib->c0_farads * res.eps_real + calib->cp_farads;
    res.capacity_pfd = total_cap * 1e12;
    res.is_valid = (res.eps_real >= 0.95);

    return res;
}
