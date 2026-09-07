#include "allan.h"
#include <math.h>
#include <stdlib.h>

void allan_cumsum(const double *rate, size_t n, double dt, double *phase) {
    if (!rate || !phase || n == 0) return;
    phase[0] = 0.0;
    for (size_t i = 0; i < n; ++i) {
        phase[i + 1] = phase[i] + rate[i] * dt;
    }
}

double allan_approx_edf(size_t n, size_t m, allan_noise_type_t noise) {
    if (m == 0 || n <= 2 * m) return 1.0;
    double N = (double)n;
    double M = (double)m;
    double edf = 1.0;

    switch (noise) {
        case ALLAN_NOISE_WFM:
            edf = (3.0 * (N - 1.0) / (2.0 * M)) - (2.0 * (N - 2.0) / N);
            break;
        case ALLAN_NOISE_FFM:
            edf = (2.0 * (N - 2.0) * (N - 2.0)) / (M * (3.0 * N - 5.0));
            break;
        case ALLAN_NOISE_RWFM:
            edf = (N - 1.0) / M;
            break;
        default:
            edf = (N - 1.0) / (2.0 * M);
            break;
    }
    return (edf < 1.0) ? 1.0 : edf;
}

/**
 * @brief Апроксимація квантиля Вілсона — Гілферті для розподілу хі-квадрат.
 */
static double chi2_quantile(double p, double v) {
    if (v < 1.0) v = 1.0;
    double z = 0.0;
    if (p >= 0.97) z = 1.95996;       /* 97.5% верхній квантиль */
    else if (p >= 0.94) z = 1.64485;  /* 95.0% квантиль */
    else if (p <= 0.03) z = -1.95996; /* 2.5% нижній квантиль */
    else if (p <= 0.06) z = -1.64485; /* 5.0% квантиль */

    double factor = 1.0 - (2.0 / (9.0 * v)) + z * sqrt(2.0 / (9.0 * v));
    if (factor < 0.0) factor = 0.0;
    return v * factor * factor * factor;
}

void allan_confidence_interval(double adev, double edf, double *ci_min, double *ci_max) {
    if (!ci_min || !ci_max) return;
    double chi2_low = chi2_quantile(0.025, edf);
    double chi2_high = chi2_quantile(0.975, edf);
    if (chi2_high <= 1e-9) chi2_high = 1e-9;
    if (chi2_low <= 1e-9) chi2_low = 1e-9;

    *ci_min = adev * sqrt(edf / chi2_high);
    *ci_max = adev * sqrt(edf / chi2_low);
}

int allan_calc_oavar(const double *phase, size_t n_phase, double dt, size_t m, allan_point_t *out) {
    if (!phase || !out || m == 0 || n_phase < 2 * m + 1) {
        return -1;
    }
    size_t num_pairs = n_phase - 2 * m;
    double sum_sq = 0.0;

    for (size_t i = 0; i < num_pairs; ++i) {
        double d2 = phase[i + 2 * m] - 2.0 * phase[i + m] + phase[i];
        sum_sq += d2 * d2;
    }

    double tau = (double)m * dt;
    double avar = sum_sq / (2.0 * (double)num_pairs * tau * tau);
    double adev = sqrt(avar);
    double edf = allan_approx_edf(n_phase - 1, m, ALLAN_NOISE_WFM);

    out->tau = tau;
    out->adev = adev;
    out->edf = edf;
    out->num_pairs = num_pairs;
    allan_confidence_interval(adev, edf, &out->adev_min, &out->adev_max);
    return 0;
}

int allan_calc_mvar(const double *phase, size_t n_phase, double dt, size_t m, allan_point_t *out) {
    if (!phase || !out || m == 0 || n_phase < 3 * m) {
        return -1;
    }
    size_t num_terms = n_phase - 3 * m + 1;
    double sum_sq = 0.0;

    /* Обчислення модифікованої дисперсії з фазовим усередненням блоком m */
    for (size_t i = 0; i < num_terms; ++i) {
        double inner_sum = 0.0;
        for (size_t j = 0; j < m; ++j) {
            double d2 = phase[i + j + 2 * m] - 2.0 * phase[i + j + m] + phase[i + j];
            inner_sum += d2;
        }
        sum_sq += inner_sum * inner_sum;
    }

    double tau = (double)m * dt;
    double m_sq = (double)m * (double)m;
    double mvar = sum_sq / (2.0 * (double)num_terms * m_sq * tau * tau);
    double mdev = sqrt(mvar);
    double edf = allan_approx_edf(n_phase - 1, m, ALLAN_NOISE_WFM);

    out->tau = tau;
    out->adev = mdev;
    out->edf = edf;
    out->num_pairs = num_terms;
    allan_confidence_interval(mdev, edf, &out->adev_min, &out->adev_max);
    return 0;
}
