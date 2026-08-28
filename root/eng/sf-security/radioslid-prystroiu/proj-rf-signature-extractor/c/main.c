#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

#define SPEED_OF_LIGHT 299792458.0
#define MAX_ITERATIONS 50
#define EPSILON 1e-5

typedef struct {
    double i;
    double q;
} complex_sample_t;

typedef struct {
    double cfo_hz;             /* Оцінка зсуву несучої частоти, Гц */
    double iq_gain_imbalance;  /* Амплітудний дисбаланс alpha = I_rms / Q_rms */
    double iq_phase_skew_deg;  /* Фазовий перекіс між гілками, градуси */
    double dc_offset_i;        /* Постійне зміщення синфазного каналу */
    double dc_offset_q;        /* Постійне зміщення квадратурного каналу */
    double snr_estimate_db;    /* Оцінка відношення сигнал/шум, дБ */
} rf_signature_t;

typedef struct {
    double x;
    double y;
} point2d_t;

typedef struct {
    point2d_t pos;
    double timestamp_s;
} tdoa_sensor_t;

/* Оцінка постійного зміщення (DC Offset) */
void estimate_dc_offset(const complex_sample_t *samples, size_t count, double *dc_i, double *dc_q) {
    double sum_i = 0.0, sum_q = 0.0;
    for (size_t k = 0; k < count; ++k) {
        sum_i += samples[k].i;
        sum_q += samples[k].q;
    }
    *dc_i = sum_i / (double)count;
    *dc_q = sum_q / (double)count;
}

/* Оцінка квадратурного дисбалансу за методом моментів (IQ Imbalance) */
void estimate_iq_imbalance(const complex_sample_t *samples, size_t count, 
                           double dc_i, double dc_q, 
                           double *gain_imb, double *phase_skew_deg) {
    double p_i = 0.0, p_q = 0.0, cross_iq = 0.0;

    for (size_t k = 0; k < count; ++k) {
        double i_centered = samples[k].i - dc_i;
        double q_centered = samples[k].q - dc_q;
        p_i += i_centered * i_centered;
        p_q += q_centered * q_centered;
        cross_iq += i_centered * q_centered;
    }

    p_i /= (double)count;
    p_q /= (double)count;
    cross_iq /= (double)count;

    if (p_q > 1e-12) {
        *gain_imb = sqrt(p_i / p_q);
    } else {
        *gain_imb = 1.0;
    }

    double denom = sqrt(p_i * p_q);
    if (denom > 1e-12) {
        double sin_phi = cross_iq / denom;
        if (sin_phi > 1.0) sin_phi = 1.0;
        if (sin_phi < -1.0) sin_phi = -1.0;
        *phase_skew_deg = asin(sin_phi) * (180.0 / M_PI);
    } else {
        *phase_skew_deg = 0.0;
    }
}

/* Оцінка зміщення частоти несучої (CFO) методом автокореляції Муза */
double estimate_cfo(const complex_sample_t *samples, size_t count, double sample_rate_hz) {
    if (count < 2) return 0.0;
    double r_re = 0.0, r_im = 0.0;

    for (size_t k = 0; k < count - 1; ++k) {
        /* r[k+1] * conj(r[k]) */
        double re1 = samples[k + 1].i, im1 = samples[k + 1].q;
        double re0 = samples[k].i,     im0 = -samples[k].q; /* conj */
        r_re += (re1 * re0 - im1 * im0);
        r_im += (re1 * im0 + im1 * re0);
    }

    double phase_diff = atan2(r_im, r_re);
    return (phase_diff * sample_rate_hz) / (2.0 * M_PI);
}

/* Повний аналіз RF-сигнатури пакета */
bool extract_rf_signature(const complex_sample_t *samples, size_t count, 
                          double sample_rate_hz, rf_signature_t *out_sig) {
    if (!samples || count < 32 || !out_sig) return false;

    estimate_dc_offset(samples, count, &out_sig->dc_offset_i, &out_sig->dc_offset_q);
    estimate_iq_imbalance(samples, count, out_sig->dc_offset_i, out_sig->dc_offset_q,
                           &out_sig->iq_gain_imbalance, &out_sig->iq_phase_skew_deg);
    out_sig->cfo_hz = estimate_cfo(samples, count, sample_rate_hz);

    /* Оцінка потужності сигналу */
    double signal_pwr = 0.0;
    for (size_t k = 0; k < count; ++k) {
        double i_c = samples[k].i - out_sig->dc_offset_i;
        double q_c = samples[k].q - out_sig->dc_offset_q;
        signal_pwr += (i_c * i_c + q_c * q_c);
    }
    signal_pwr /= (double)count;
    out_sig->snr_estimate_db = 10.0 * log10(signal_pwr + 1e-12);

    return true;
}

/* Двовимірна локалізація TDoA методом Гаусса-Ньютона */
bool solve_tdoa_2d(const tdoa_sensor_t *sensors, size_t sensor_count, 
                   point2d_t initial_guess, point2d_t *out_pos) {
    if (!sensors || sensor_count < 3 || !out_pos) return false;

    double x = initial_guess.x;
    double y = initial_guess.y;

    for (int iter = 0; iter < MAX_ITERATIONS; ++iter) {
        double d0 = sqrt((x - sensors[0].pos.x) * (x - sensors[0].pos.x) + 
                         (y - sensors[0].pos.y) * (y - sensors[0].pos.y));
        if (d0 < 1e-4) d0 = 1e-4;

        /* J^T * J (розмір 2x2) та J^T * r (розмір 2x1) */
        double jtj00 = 0.0, jtj01 = 0.0, jtj11 = 0.0;
        double jtr0 = 0.0, jtr1 = 0.0;

        for (size_t i = 1; i < sensor_count; ++i) {
            double di = sqrt((x - sensors[i].pos.x) * (x - sensors[i].pos.x) + 
                             (y - sensors[i].pos.y) * (y - sensors[i].pos.y));
            if (di < 1e-4) di = 1e-4;

            double measured_delta_d = SPEED_OF_LIGHT * (sensors[i].timestamp_s - sensors[0].timestamp_s);
            double calculated_delta_d = di - d0;
            double residual = measured_delta_d - calculated_delta_d;

            double j_x = ((x - sensors[i].pos.x) / di) - ((x - sensors[0].pos.x) / d0);
            double j_y = ((y - sensors[i].pos.y) / di) - ((y - sensors[0].pos.y) / d0);

            jtj00 += j_x * j_x;
            jtj01 += j_x * j_y;
            jtj11 += j_y * j_y;

            jtr0 += j_x * residual;
            jtr1 += j_y * residual;
        }

        double det = jtj00 * jtj11 - jtj01 * jtj01;
        if (fabs(det) < 1e-12) return false; /* Погано обумовлена матриця (колінеарність) */

        double inv00 = jtj11 / det;
        double inv01 = -jtj01 / det;
        double inv11 = jtj00 / det;

        double delta_x = inv00 * jtr0 + inv01 * jtr1;
        double delta_y = inv01 * jtr0 + inv11 * jtr1;

        x += delta_x;
        y += delta_y;

        if (sqrt(delta_x * delta_x + delta_y * delta_y) < EPSILON) {
            out_pos->x = x;
            out_pos->y = y;
            return true;
        }
    }

    out_pos->x = x;
    out_pos->y = y;
    return true;
}

int main(void) {
    /* Генерація тестового сигналу з апаратним дисбалансом */
    const size_t N = 128;
    complex_sample_t test_signal[128];
    const double Fs = 10000000.0; /* 10 MSps */
    const double True_CFO = 45200.0; /* 45.2 кГц */

    for (size_t k = 0; k < N; ++k) {
        double t = (double)k / Fs;
        double phase = 2.0 * M_PI * True_CFO * t;
        /* I-гілка: коефіцієнт 1.06, зміщення 0.03 */
        test_signal[k].i = 1.06 * cos(phase) + 0.03;
        /* Q-гілка: коефіцієнт 0.94, зсув фази +4 град, зміщення -0.02 */
        test_signal[k].q = 0.94 * sin(phase + 4.0 * M_PI / 180.0) - 0.02;
    }

    rf_signature_t sig;
    if (extract_rf_signature(test_signal, N, Fs, &sig)) {
        printf("RF Fingerprint Extracted:\n");
        printf("  CFO: %.1f Hz\n", sig.cfo_hz);
        printf("  IQ Gain Imbalance: %.4f\n", sig.iq_gain_imbalance);
        printf("  IQ Phase Skew: %.2f deg\n", sig.iq_phase_skew_deg);
        printf("  DC Offset: I=%.3f, Q=%.3f\n", sig.dc_offset_i, sig.dc_offset_q);
    }

    /* Тест TDoA локалізації з 3 станціями */
    tdoa_sensor_t network[3] = {
        { .pos = { .x = 0.0,    .y = 0.0 },    .timestamp_s = 0.000001000 },
        { .pos = { .x = 1000.0, .y = 0.0 },    .timestamp_s = 0.000002155 },
        { .pos = { .x = 500.0,  .y = 1000.0 }, .timestamp_s = 0.000001840 }
    };

    point2d_t guess = { .x = 500.0, .y = 500.0 };
    point2d_t estimated_target;
    if (solve_tdoa_2d(network, 3, guess, &estimated_target)) {
        printf("TDoA Estimated Target: X=%.2f m, Y=%.2f m\n", 
               estimated_target.x, estimated_target.y);
    }

    return 0;
}
