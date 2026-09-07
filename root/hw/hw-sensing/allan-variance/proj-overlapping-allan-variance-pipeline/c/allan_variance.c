#include "allan_variance.h"
#include <math.h>
#include <stdlib.h>

void allan_compute_phase(const double *y, size_t n, double dt, double *theta_out) {
    if (!y || !theta_out || n == 0) {
        return;
    }
    theta_out[0] = 0.0;
    for (size_t i = 0; i < n; ++i) {
        theta_out[i + 1] = theta_out[i] + y[i] * dt;
    }
}

double allan_compute_oadev(const double *theta, size_t n, double dt, size_t m) {
    if (!theta || n < 2 * m + 1 || m == 0) {
        return 0.0;
    }

    const double tau = (double)m * dt;
    const size_t limit = n - 2 * m;
    double sum_sq = 0.0;

    /* Швидке обчислення другої різниці фази без динамічного виділення пам'яті */
    for (size_t k = 0; k < limit; ++k) {
        /* delta2_theta = theta[k + 2m] - 2 * theta[k + m] + theta[k] */
        const double diff = theta[k + 2 * m] - 2.0 * theta[k + m] + theta[k];
        sum_sq += diff * diff;
    }

    const double oavar = sum_sq / (2.0 * tau * tau * (double)limit);
    return sqrt(oavar);
}

double allan_compute_mdev(const double *theta, size_t n, double dt, size_t m) {
    if (!theta || n < 3 * m || m == 0) {
        return 0.0;
    }

    const double tau = (double)m * dt;
    const size_t num_terms = n - 3 * m + 1;
    double sum_sq = 0.0;

    /* Обчислення початкового ковзного сумарного вікна розміром m */
    double running_sum = 0.0;
    for (size_t i = 0; i < m; ++i) {
        running_sum += (theta[i + 2 * m] - 2.0 * theta[i + m] + theta[i]);
    }
    sum_sq += running_sum * running_sum;

    /* Ковзне оновлення за O(1) на кожному кроці j */
    for (size_t j = 1; j < num_terms; ++j) {
        const double leaving = theta[j - 1 + 2 * m] - 2.0 * theta[j - 1 + m] + theta[j - 1];
        const double entering = theta[j + 3 * m - 1] - 2.0 * theta[j + 2 * m - 1] + theta[j + m - 1];
        running_sum += (entering - leaving);
        sum_sq += running_sum * running_sum;
    }

    const double norm = 2.0 * (double)m * (double)m * tau * tau * (double)num_terms;
    const double mvar = sum_sq / norm;
    return sqrt(mvar);
}

void allan_compute_confidence_interval(double adev, size_t n, size_t m,
                                       double *out_edf, double *out_lower, double *out_upper) {
    if (n <= 2 * m || m == 0 || adev <= 0.0) {
        if (out_edf) *out_edf = 1.0;
        if (out_lower) *out_lower = adev;
        if (out_upper) *out_upper = adev;
        return;
    }

    /* Апроксимація ефективних ступенів вільності (EDF) для білого шуму (IEEE 952 / Greenhall) */
    const double n_f = (double)n;
    const double m_f = (double)m;
    double edf = (3.0 * (n_f - 1.0) / (2.0 * m_f) - (n_f - 2.0) / n_f) * (4.0 * m_f * m_f) / (4.0 * m_f * m_f + 5.0);
    if (edf < 1.0) {
        edf = 1.0;
    }

    /* Апроксимація квантилів розподілу хі-квадрат за методом Вілсона-Гілферті для 95% довіри (z = 1.96) */
    const double z = 1.959964;
    const double factor = 2.0 / (9.0 * edf);
    const double term_low = 1.0 - factor - z * sqrt(factor);
    const double term_high = 1.0 - factor + z * sqrt(factor);

    const double chi2_lower_p = edf * (term_low > 0.01 ? term_low * term_low * term_low : 0.0001);
    const double chi2_upper_p = edf * (term_high * term_high * term_high);

    if (out_edf) *out_edf = edf;
    if (out_lower) *out_lower = adev * sqrt(edf / chi2_upper_p);
    if (out_upper) *out_upper = adev * sqrt(edf / chi2_lower_p);
}

bool allan_analyze_pipeline(const double *y, size_t n, double dt,
                            const size_t *m_list, size_t num_taus,
                            AllanResult *results_out) {
    if (!y || !m_list || !results_out || n < 4 || num_taus == 0 || dt <= 0.0) {
        return false;
    }

    /* Виділяємо буфер фази один раз перед циклом */
    double *theta = (double *)malloc((n + 1) * sizeof(double));
    if (!theta) {
        return false;
    }

    allan_compute_phase(y, n, dt, theta);

    for (size_t i = 0; i < num_taus; ++i) {
        const size_t m = m_list[i];
        results_out[i].m = m;
        results_out[i].tau = (double)m * dt;

        if (n >= 2 * m + 1) {
            results_out[i].adev = allan_compute_oadev(theta, n, dt, m);
            allan_compute_confidence_interval(results_out[i].adev, n, m,
                                              &results_out[i].edf,
                                              &results_out[i].adev_lower,
                                              &results_out[i].adev_upper);
        } else {
            results_out[i].adev = 0.0;
            results_out[i].edf = 0.0;
            results_out[i].adev_lower = 0.0;
            results_out[i].adev_upper = 0.0;
        }

        if (n >= 3 * m) {
            results_out[i].mdev = allan_compute_mdev(theta, n, dt, m);
        } else {
            results_out[i].mdev = 0.0;
        }
    }

    free(theta);
    return true;
}
