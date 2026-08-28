#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

typedef struct {
    float i;
    float q;
} iq_sample_t;

typedef struct {
    double cfo_hz;
    double gain_imbalance;
    double phase_skew_deg;
    double dc_offset_i;
    double dc_offset_q;
    double snr_db;
} rf_emitter_metrics_t;

/* Обчислення вектора радіочастотних ознак передавача */
bool compute_rf_metrics(const iq_sample_t *samples, size_t count, 
                        double sample_rate, rf_emitter_metrics_t *out) {
    if (!samples || count < 64 || !out) return false;

    /* 1. Постійне зміщення (DC Offset) */
    double sum_i = 0.0, sum_q = 0.0;
    for (size_t k = 0; k < count; ++k) {
        sum_i += samples[k].i;
        sum_q += samples[k].q;
    }
    out->dc_offset_i = sum_i / (double)count;
    out->dc_offset_q = sum_q / (double)count;

    /* 2. Квадратурний дисбаланс (IQ Imbalance) */
    double p_i = 0.0, p_q = 0.0, cross_iq = 0.0;
    for (size_t k = 0; k < count; ++k) {
        double ci = samples[k].i - out->dc_offset_i;
        double cq = samples[k].q - out->dc_offset_q;
        p_i += ci * ci;
        p_q += cq * cq;
        cross_iq += ci * cq;
    }
    p_i /= (double)count;
    p_q /= (double)count;
    cross_iq /= (double)count;

    out->gain_imbalance = (p_q > 1e-12) ? sqrt(p_i / p_q) : 1.0;
    double denom = sqrt(p_i * p_q);
    if (denom > 1e-12) {
        double s = cross_iq / denom;
        if (s > 1.0) s = 1.0;
        if (s < -1.0) s = -1.0;
        out->phase_skew_deg = asin(s) * (180.0 / M_PI);
    } else {
        out->phase_skew_deg = 0.0;
    }

    /* 3. Зсув частоти несучої (CFO) через диференційну автокореляцію */
    double re_acc = 0.0, im_acc = 0.0;
    for (size_t k = 0; k < count - 1; ++k) {
        double r1_re = samples[k + 1].i, r1_im = samples[k + 1].q;
        double r0_re = samples[k].i,     r0_im = -samples[k].q; /* conj */
        re_acc += (r1_re * r0_re - r1_im * r0_im);
        im_acc += (r1_re * r0_im + r1_im * r0_re);
    }
    double phase_step = atan2(im_acc, re_acc);
    out->cfo_hz = (phase_step * sample_rate) / (2.0 * M_PI);

    /* 4. Оцінка відношення сигнал/шум */
    out->snr_db = 10.0 * log10((p_i + p_q) + 1e-12);

    return true;
}
