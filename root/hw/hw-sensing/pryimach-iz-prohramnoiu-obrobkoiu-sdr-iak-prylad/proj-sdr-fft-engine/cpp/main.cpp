#include <vector>
#include <span>
#include <complex>
#include <cmath>
#include <numbers>
#include <algorithm>
#include <stdexcept>

struct PeakResult {
    float bin_index;
    float power_dbm;
};

class SdrSpectrumAnalyzer {
public:
    explicit SdrSpectrumAnalyzer(size_t size, float cal_offset_db = 0.0f, float alpha = 0.2f)
        : size_(size), cal_offset_db_(cal_offset_db), alpha_(alpha),
          window_(size), twiddles_(size / 2), fft_buffer_(size), 
          power_spectrum_dbm_(size), averaged_spectrum_(size, -140.0f) {
        if ((size & (size - 1)) != 0 || size == 0) {
            throw std::invalid_argument("FFT size must be a power of two");
        }
        init_blackman_harris();
        init_twiddles();
    }

    void process(std::span<const std::complex<float>> input) {
        if (input.size() != size_) {
            throw std::invalid_argument("Input size mismatch");
        }

        // 1. Віконне зважування
        for (size_t i = 0; i < size_; ++i) {
            fft_buffer_[i] = input[i] * window_[i];
        }

        // 2. Комплексне FFT
        radix2_fft(fft_buffer_, twiddles_);

        // 3. fftshift, розрахунок потужності в dBm та відеоусереднення
        const size_t half = size_ / 2;
        for (size_t i = 0; i < size_; ++i) {
            size_t shifted_idx = (i < half) ? (i + half) : (i - half);
            float power_lin = std::norm(fft_buffer_[i]);
            power_lin = std::max(power_lin, 1e-18f);

            float power_dbm = 10.0f * std::log10(power_lin) + cal_offset_db_;
            power_spectrum_dbm_[shifted_idx] = power_dbm;

            averaged_spectrum_[shifted_idx] =
                alpha_ * power_dbm + (1.0f - alpha_) * averaged_spectrum_[shifted_idx];
        }
    }

    [[nodiscard]] std::span<const float> power_spectrum() const noexcept {
        return power_spectrum_dbm_;
    }

    [[nodiscard]] std::span<const float> averaged_spectrum() const noexcept {
        return averaged_spectrum_;
    }

    [[nodiscard]] PeakResult find_peak_interpolated() const noexcept {
        auto it = std::max_element(averaged_spectrum_.begin() + 1, averaged_spectrum_.end() - 1);
        size_t max_idx = std::distance(averaged_spectrum_.begin(), it);

        float y_left = averaged_spectrum_[max_idx - 1];
        float y_mid = averaged_spectrum_[max_idx];
        float y_right = averaged_spectrum_[max_idx + 1];

        float denom = y_left - 2.0f * y_mid + y_right;
        float delta = 0.0f;
        if (std::abs(denom) > 1e-6f) {
            delta = 0.5f * (y_left - y_right) / denom;
        }

        return {
            .bin_index = static_cast<float>(max_idx) + delta,
            .power_dbm = y_mid - 0.25f * (y_left - y_right) * delta
        };
    }

private:
    void init_blackman_harris() {
        constexpr float a0 = 0.35875f;
        constexpr float a1 = 0.48829f;
        constexpr float a2 = 0.14128f;
        constexpr float a3 = 0.01168f;
        const float pi = std::numbers::pi_v<float>;

        for (size_t i = 0; i < size_; ++i) {
            float theta = (2.0f * pi * static_cast<float>(i)) / static_cast<float>(size_ - 1);
            window_[i] = a0 - a1 * std::cos(theta) + a2 * std::cos(2.0f * theta) - a3 * std::cos(3.0f * theta);
        }
    }

    void init_twiddles() {
        const float pi = std::numbers::pi_v<float>;
        for (size_t i = 0; i < size_ / 2; ++i) {
            float angle = -2.0f * pi * static_cast<float>(i) / static_cast<float>(size_);
            twiddles_[i] = std::complex<float>(std::cos(angle), std::sin(angle));
        }
    }

    static void radix2_fft(std::vector<std::complex<float>>& x, 
                           const std::vector<std::complex<float>>& twiddles) {
        const size_t n = x.size();
        size_t j = 0;
        for (size_t i = 0; i < n - 1; ++i) {
            if (i < j) {
                std::swap(x[i], x[j]);
            }
            size_t k = n >> 1;
            while (k <= j) {
                j -= k;
                k >>= 1;
            }
            j += k;
        }

        for (size_t len = 2; len <= n; len <<= 1) {
            size_t half_len = len >> 1;
            size_t step = n / len;
            for (size_t i = 0; i < n; i += len) {
                for (size_t m = 0; m < half_len; ++m) {
                    std::complex<float> w = twiddles[m * step];
                    std::complex<float> u = x[i + m];
                    std::complex<float> v = x[i + m + half_len] * w;
                    x[i + m] = u + v;
                    x[i + m + half_len] = u - v;
                }
            }
        }
    }

    size_t size_;
    float cal_offset_db_;
    float alpha_;
    std::vector<float> window_;
    std::vector<std::complex<float>> twiddles_;
    std::vector<std::complex<float>> fft_buffer_;
    std::vector<float> power_spectrum_dbm_;
    std::vector<float> averaged_spectrum_;
};
