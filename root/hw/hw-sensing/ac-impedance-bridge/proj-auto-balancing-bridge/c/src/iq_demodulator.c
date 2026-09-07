#include "iq_demodulator.h"
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

bool iq_demodulator_init(iq_demodulator_t *demod, double sample_rate_hz, double signal_freq_hz) {
    if (!demod || sample_rate_hz <= 0.0 || signal_freq_hz <= 0.0) {
        return false;
    }
    /* Теорема Найквіста: частота дискретизації має перевищувати подвійну частоту сигналу */
    if (sample_rate_hz < 2.0 * signal_freq_hz) {
        return false;
    }

    demod->sample_rate_hz = sample_rate_hz;
    demod->signal_freq_hz = signal_freq_hz;
    demod->samples_per_period = (size_t)llround(sample_rate_hz / signal_freq_hz);
    
    iq_demodulator_reset(demod);
    return true;
}

void iq_demodulator_reset(iq_demodulator_t *demod) {
    if (!demod) return;
    demod->total_samples = 0;
    demod->sum_v_i = 0.0;
    demod->sum_v_q = 0.0;
    demod->sum_i_i = 0.0;
    demod->sum_i_q = 0.0;
}

void iq_demodulator_feed(iq_demodulator_t *demod, double v_sample, double i_sample) {
    if (!demod) return;

    /* Обчислення фази поточного дискретного моменту часу */
    double time_sec = (double)demod->total_samples / demod->sample_rate_hz;
    double phase = 2.0 * M_PI * demod->signal_freq_hz * time_sec;

    /* Опорні квадратурні сигнали */
    double ref_sin = sin(phase);
    double ref_cos = cos(phase);

    /* Синхронне перемноження та накопичення сум */
    demod->sum_v_i += v_sample * ref_cos;
    demod->sum_v_q += v_sample * ref_sin;

    demod->sum_i_i += i_sample * ref_cos;
    demod->sum_i_q += i_sample * ref_sin;

    demod->total_samples++;
}

void iq_demodulator_process_block(iq_demodulator_t *demod, 
                                 const double *v_samples, 
                                 const double *i_samples, 
                                 size_t count) {
    if (!demod || !v_samples || !i_samples) return;
    for (size_t k = 0; k < count; ++k) {
        iq_demodulator_feed(demod, v_samples[k], i_samples[k]);
    }
}

bool iq_demodulator_calculate(const iq_demodulator_t *demod, impedance_result_t *result) {
    if (!demod || !result || demod->total_samples == 0) {
        return false;
    }

    /* Нормування накопичених сум інтегрування (коефіцієнт 2/N для амплітуд) */
    double norm_factor = 2.0 / (double)demod->total_samples;
    
    double v_i = demod->sum_v_i * norm_factor;
    double v_q = demod->sum_v_q * norm_factor;
    double i_i = demod->sum_i_i * norm_factor;
    double i_q = demod->sum_i_q * norm_factor;

    /* Квадрат модуля комплексного струму |I|^2 = I_real^2 + I_imag^2 */
    double i_magnitude_sq = i_i * i_i + i_q * i_q;
    if (i_magnitude_sq < 1e-18) {
        /* Струм практично нульовий (розімкнене коло) */
        return false;
    }

    /* Комплексне ділення Z = V / I = (V_i + j*V_q) / (I_i + j*I_q)
     * Z_real = (V_i * I_i + V_q * I_q) / |I|^2
     * Z_imag = (V_q * I_i - V_i * I_q) / |I|^2 */
    double z_real = (v_i * i_i + v_q * i_q) / i_magnitude_sq;
    double z_imag = (v_q * i_i - v_i * i_q) / i_magnitude_sq;

    result->r_real = z_real;
    result->x_imag = z_imag;
    result->z_magnitude = sqrt(z_real * z_real + z_imag * z_imag);
    result->phase_rad = atan2(z_imag, z_real);
    result->phase_deg = result->phase_rad * (180.0 / M_PI);

    /* Розрахунок добротності Q та тангенса кута втрат D */
    double abs_real = fabs(z_real);
    double abs_imag = fabs(z_imag);

    if (abs_real > 1e-9) {
        result->quality_fac = abs_imag / abs_real;
    } else {
        result->quality_fac = 1e6;
    }

    if (abs_imag > 1e-9) {
        result->dissipation = abs_real / abs_imag;
    } else {
        result->dissipation = 1e6;
    }

    return true;
}
