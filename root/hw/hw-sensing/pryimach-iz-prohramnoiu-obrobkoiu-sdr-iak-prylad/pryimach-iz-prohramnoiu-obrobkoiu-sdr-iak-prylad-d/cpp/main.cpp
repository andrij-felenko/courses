#include <vector>
#include <span>
#include <complex>
#include <cmath>
#include <numbers>
#include <algorithm>

/* Обчислення спектра потужності в dBm із вікном Blackman-Harris */
std::vector<float> compute_spectrum_dbm(std::span<const std::complex<float>> iq_in,
                                        float v_fs_volts, float cal_gain_db) {
    const size_t n = iq_in.size();
    const size_t half = n / 2;
    std::vector<std::complex<float>> win_buf(n);
    std::vector<float> spec_dbm_out(n);

    constexpr float a0 = 0.35875f, a1 = 0.48829f, a2 = 0.14128f, a3 = 0.01168f;
    const float pi = std::numbers::pi_v<float>;
    float s1 = 0.0f;

    // 1. Віконне зважування та накопичення S1
    for (size_t i = 0; i < n; ++i) {
        float theta = (2.0f * pi * static_cast<float>(i)) / static_cast<float>(n - 1);
        float w = a0 - a1 * std::cos(theta) + a2 * std::cos(2.0f * theta) - a3 * std::cos(3.0f * theta);
        win_buf[i] = iq_in[i] * w;
        s1 += w;
    }

    // 2. Виклик FFT (наприклад, внутрішнього Radix-2)
    // radix2_fft(win_buf);

    // 3. Масштабування в dBm та fftshift
    const float p_ref_mw = 10.0f * (v_fs_volts * v_fs_volts);
    const float norm_factor = 1.0f / (s1 * s1);

    for (size_t k = 0; k < n; ++k) {
        size_t shifted_idx = (k < half) ? (k + half) : (k - half);
        float mag_sq = std::norm(win_buf[k]);
        float power_mw = mag_sq * norm_factor * p_ref_mw;
        power_mw = std::max(power_mw, 1e-15f);

        spec_dbm_out[shifted_idx] = 10.0f * std::log10(power_mw) + cal_gain_db;
    }

    return spec_dbm_out;
}
