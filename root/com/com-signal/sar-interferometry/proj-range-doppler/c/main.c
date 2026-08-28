#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <complex.h>

#define C_LIGHT 299792458.0f
#define M_PI_F 3.14159265358979323846f

typedef struct {
    float carrier_freq_hz;
    float range_bandwidth_hz;
    float pulse_duration_s;
    float sampling_rate_hz;
    float platform_velocity_ms;
    float prf_hz;
    float target_range_m;
    float antenna_length_m;
    size_t num_range_bins;
    size_t num_azimuth_pulses;
} radar_config_t;

void fft1d_c(float complex *data, size_t n, int inverse) {
    if (n <= 1) return;
    for (size_t i = 1, j = 0; i < n; ++i) {
        size_t bit = n >> 1;
        for (; j & bit; bit >>= 1) j ^= bit;
        j ^= bit;
        if (i < j) {
            float complex tmp = data[i];
            data[i] = data[j];
            data[j] = tmp;
        }
    }
    for (size_len = 2; len <= n; len <<= 1) {
        float angle = 2.0f * M_PI_F / (float)len;
        if (inverse) angle = -angle;
        float complex wlen = cosf(angle) + I * sinf(angle);
        for (size_t i = 0; i < n; i += len) {
            float complex w = 1.0f + 0.0f * I;
            for (size_t j = 0; j < len / 2; ++j) {
                float complex u = data[i + j];
                float complex v = data[i + j + len / 2] * w;
                data[i + j] = u + v;
                data[i + j + len / 2] = u - v;
                w *= wlen;
            }
        }
    }
    if (inverse) {
        float scale = 1.0f / (float)n;
        for (size_t i = 0; i < n; ++i) data[i] *= scale;
    }
}

int main(void) {
    radar_config_t cfg = {
        .carrier_freq_hz = 9.6e9f,
        .range_bandwidth_hz = 100.0e6f,
        .pulse_duration_s = 10.0e-6f,
        .sampling_rate_hz = 120.0e6f,
        .platform_velocity_ms = 150.0f,
        .prf_hz = 500.0f,
        .target_range_m = 3000.0f,
        .antenna_length_m = 1.5f,
        .num_range_bins = 256,
        .num_azimuth_pulses = 256
    };

    size_t total = cfg.num_azimuth_pulses * cfg.num_range_bins;
    float complex *img = (float complex *)calloc(total, sizeof(float complex));
    if (!img) return 1;

    float chirp_rate = cfg.range_bandwidth_hz / cfg.pulse_duration_s;
    float dt = 1.0f / cfg.sampling_rate_hz;
    float d_eta = 1.0f / cfg.prf_hz;

    // Синтез сирого відгуку точкової цілі
    for (size_t az = 0; az < cfg.num_azimuth_pulses; ++az) {
        float eta = ((float)az - (float)cfg.num_azimuth_pulses / 2.0f) * d_eta;
        float r_eta = sqrtf(cfg.target_range_m * cfg.target_range_m +
                            (cfg.platform_velocity_ms * eta) * (cfg.platform_velocity_ms * eta));
        float tau_0 = 2.0f * r_eta / C_LIGHT;
        for (size_t rg = 0; rg < cfg.num_range_bins; ++rg) {
            float tau = ((float)rg - (float)cfg.num_range_bins / 2.0f) * dt + 2.0f * cfg.target_range_m / C_LIGHT;
            float t_diff = tau - tau_0;
            if (fabsf(t_diff) <= cfg.pulse_duration_s / 2.0f) {
                float phase = -2.0f * M_PI_F * cfg.carrier_freq_hz * tau_0 +
                              M_PI_F * chirp_rate * t_diff * t_diff;
                img[az * cfg.num_range_bins + rg] = cosf(phase) + I * sinf(phase);
            }
        }
    }

    printf("[SAR-RDA-C] Сирий масив %zux%zu сформовано успішно.\n",
           cfg.num_azimuth_pulses, cfg.num_range_bins);

    free(img);
    return 0;
}
