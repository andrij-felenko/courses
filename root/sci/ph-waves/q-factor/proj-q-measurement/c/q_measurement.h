/* q_measurement.h — C-бібліотека обчислення добротності */
#ifndef Q_MEASUREMENT_H
#define Q_MEASUREMENT_H

#include <stddef.h>
#include <math.h>
#include <stdbool.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef struct {
    double q_factor;
    double r_squared;      /* Коефіцієнт детермінації R² для оцінки якості апроксимації */
    double initial_amp;
    bool valid;
} q_ringdown_result_t;

typedef struct {
    double q_factor;
    double f0_hz;
    double bandwidth_hz;
    bool valid;
} q_bandwidth_result_t;

/* Обчислення Q методом МНК-регресії логарифма огинаючої спаду */
q_ringdown_result_t measure_q_ringdown(
    const double *samples, 
    size_t count, 
    double sample_rate_hz, 
    double f0_hz,
    double noise_floor
) {
    q_ringdown_result_t res = {0.0, 0.0, 0.0, false};
    if (!samples || count < 10 || sample_rate_hz <= 0.0 || f0_hz <= 0.0) {
        return res;
    }

    /* Знаходження локальних піків */
    size_t peak_count = 0;
    double sum_t = 0.0, sum_y = 0.0, sum_tt = 0.0, sum_ty = 0.0;

    for (size_t i = 1; i < count - 1; ++i) {
        if (samples[i] > samples[i - 1] && samples[i] > samples[i + 1] && samples[i] > noise_floor) {
            double t = (double)i / sample_rate_hz;
            double y = log(samples[i]);

            sum_t += t;
            sum_y += y;
            sum_tt += t * t;
            sum_ty += t * y;
            peak_count++;
        }
    }

    if (peak_count < 3) {
        return res; /* Занадто мало піків для регресії */
    }

    double n = (double)peak_count;
    double denom = (n * sum_tt - sum_t * sum_t);
    if (fabs(denom) < 1e-12) {
        return res;
    }

    double slope = (n * sum_ty - sum_t * sum_y) / denom;
    double intercept = (sum_y - slope * sum_t) / n;

    if (slope >= 0.0) {
        return res; /* Нахил має бути від'ємним для загасання */
    }

    /* Обчислення R² */
    double mean_y = sum_y / n;
    double ss_tot = 0.0, ss_res = 0.0;

    for (size_t i = 1; i < count - 1; ++i) {
        if (samples[i] > samples[i - 1] && samples[i] > samples[i + 1] && samples[i] > noise_floor) {
            double t = (double)i / sample_rate_hz;
            double y = log(samples[i]);
            double y_pred = intercept + slope * t;
            ss_tot += (y - mean_y) * (y - mean_y);
            ss_res += (y - y_pred) * (y - y_pred);
        }
    }

    res.q_factor = -(M_PI * f0_hz) / slope;
    res.initial_amp = exp(intercept);
    res.r_squared = (ss_tot > 0.0) ? (1.0 - (ss_res / ss_tot)) : 0.0;
    res.valid = (res.r_squared > 0.85);

    return res;
}

/* Обчислення Q за спектром методом -3 дБ */
q_bandwidth_result_t measure_q_bandwidth(
    const double *spectrum_amp, 
    const double *freqs_hz, 
    size_t count
) {
    q_bandwidth_result_t res = {0.0, 0.0, 0.0, false};
    if (!spectrum_amp || !freqs_hz || count < 5) {
        return res;
    }

    /* Пошук максимуму */
    size_t max_idx = 0;
    double max_amp = spectrum_amp[0];
    for (size_t i = 1; i < count; ++i) {
        if (spectrum_amp[i] > max_amp) {
            max_amp = spectrum_amp[i];
            max_idx = i;
        }
    }

    if (max_amp <= 0.0 || max_idx == 0 || max_idx == count - 1) {
        return res;
    }

    double target_amp = max_amp / sqrt(2.0);

    /* Ліва точка f1 */
    double f1 = freqs_hz[0];
    for (size_t i = max_idx; i > 0; --i) {
        if (spectrum_amp[i - 1] <= target_amp) {
            double a1 = spectrum_amp[i - 1];
            double a2 = spectrum_amp[i];
            double f_left = freqs_hz[i - 1];
            double f_right = freqs_hz[i];
            f1 = f_left + (target_amp - a1) * (f_right - f_left) / (a2 - a1);
            break;
        }
    }

    /* Права точка f2 */
    double f2 = freqs_hz[count - 1];
    for (size_t i = max_idx; i < count - 1; ++i) {
        if (spectrum_amp[i + 1] <= target_amp) {
            double a1 = spectrum_amp[i];
            double a2 = spectrum_amp[i + 1];
            double f_left = freqs_hz[i];
            double f_right = freqs_hz[i + 1];
            f2 = f_left + (target_amp - a1) * (f_right - f_left) / (a2 - a1);
            break;
        }
    }

    double bw = f2 - f1;
    if (bw <= 0.0) {
        return res;
    }

    res.f0_hz = freqs_hz[max_idx];
    res.bandwidth_hz = bw;
    res.q_factor = res.f0_hz / bw;
    res.valid = true;

    return res;
}
#endif
