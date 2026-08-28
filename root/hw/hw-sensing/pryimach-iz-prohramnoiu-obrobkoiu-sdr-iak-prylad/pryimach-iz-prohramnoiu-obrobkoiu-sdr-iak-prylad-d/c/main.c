#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef struct {
    float i;
    float q;
} complex_f32_t;

/* Обчислення спектра потужності в dBm із вікном Blackman-Harris */
void compute_spectrum_dbm(const complex_f32_t *iq_in, float *spec_dbm_out, 
                          size_t n, float v_fs_volts, float cal_gain_db) {
    /* 1. Розрахунок вікна та когерентної суми S1 */
    float s1 = 0.0f;
    const float a0 = 0.35875f, a1 = 0.48829f, a2 = 0.14128f, a3 = 0.01168f;
    
    complex_f32_t *win_buf = (complex_f32_t*)malloc(n * sizeof(complex_f32_t));
    if (!win_buf) return;

    for (size_t i = 0; i < n; ++i) {
        float theta = (2.0f * (float)M_PI * (float)i) / (float)(n - 1);
        float w = a0 - a1 * cosf(theta) + a2 * cosf(2.0f * theta) - a3 * cosf(3.0f * theta);
        win_buf[i].i = iq_in[i].i * w;
        win_buf[i].q = iq_in[i].q * w;
        s1 += w;
    }

    /* 2. ДПФ / FFT (пряме перетворення) */
    /* У реальній системі викликається radix2_fft(win_buf, n) */

    /* 3. Масштабування в dBm з центруванням fftshift */
    const size_t half = n / 2;
    const float p_ref_mw = 10.0f * (v_fs_volts * v_fs_volts); /* 50 Ом навантаження */
    const float norm_factor = 1.0f / (s1 * s1);

    for (size_t k = 0; k < n; ++k) {
        size_t shifted_idx = (k < half) ? (k + half) : (k - half);
        float mag_sq = win_buf[k].i * win_buf[k].i + win_buf[k].q * win_buf[k].q;
        float power_mw = mag_sq * norm_factor * p_ref_mw;
        
        if (power_mw < 1e-15f) power_mw = 1e-15f; /* Поріг відсікання -150 dBm */
        spec_dbm_out[shifted_idx] = 10.0f * log10f(power_mw) + cal_gain_db;
    }

    free(win_buf);
}
