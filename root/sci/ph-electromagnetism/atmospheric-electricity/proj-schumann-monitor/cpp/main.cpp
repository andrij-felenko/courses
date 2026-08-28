// 
// DSP модуль моніторингу резонансів Шумана (Мова C++20)
// 

#include <iostream>
#include <vector>
#include <complex>
#include <cmath>
#include <numbers>
#include <optional>
#include <span>
#include <algorithm>
#include <numeric>

namespace dsp::schumann {

constexpr float kDefaultSampleRateHz = 256.0f;
constexpr size_t kDefaultWindowSize  = 1024;

struct PeakInfo {
    float frequency_hz{0.0f};
    float amplitude_psd{0.0f};
    float quality_factor{0.0f};
};

struct SchumannAnalysisResult {
    std::optional<PeakInfo> n1_peak;
    std::optional<PeakInfo> n2_peak;
    std::optional<PeakInfo> n3_peak;
};

class SchumannAnalyzer {
public:
    explicit SchumannAnalyzer(size_t window_size = kDefaultWindowSize, 
                             float sample_rate_hz = kDefaultSampleRateHz)
        : window_size_(window_size)
        , sample_rate_(sample_rate_hz)
        , window_coeffs_(window_size)
    {
        init_hann_window();
    }

    [[nodiscard]] std::optional<SchumannAnalysisResult> analyze(std::span<const float> raw_samples) const {
        if (raw_samples.size() != window_size_) {
            return std::nullopt;
        }

        // 1. Видалення DC зміщення через std::accumulate
        const float mean = std::accumulate(raw_samples.begin(), raw_samples.end(), 0.0f) 
                           / static_cast<float>(window_size_);

        std::vector<float> windowed_signal(window_size_);
        for (size_t i = 0; i < window_size_; ++i) {
            windowed_signal[i] = (raw_samples[i] - mean) * window_coeffs_[i];
        }

        // 2. Обчислення PSD для цікавого діапазону частот (0-45 Гц)
        const size_t max_bin = static_cast<size_t>(std::lround((45.0f * window_size_) / sample_rate_));
        std::vector<float> psd(max_bin + 1);
        const float norm_scale = 2.0f / (sample_rate_ * window_energy_sum_);

        for (size_t k = 0; k <= max_bin; ++k) {
            std::complex<float> bin_val{0.0f, 0.0f};
            const float angle_step = -2.0f * std::numbers::pi_v<float> * static_cast<float>(k) 
                                     / static_cast<float>(window_size_);

            for (size_t n = 0; n < window_size_; ++n) {
                const float angle = angle_step * static_cast<float>(n);
                bin_val += windowed_signal[n] * std::polar(1.0f, angle);
            }
            psd[k] = norm_scale * std::norm(bin_val);
        }

        // 3. Виявлення піків перших трьох гармонік
        SchumannAnalysisResult result;
        result.n1_peak = extract_peak(psd, 6.0f, 10.0f);
        result.n2_peak = extract_peak(psd, 12.0f, 16.0f);
        result.n3_peak = extract_peak(psd, 18.0f, 24.0f);

        return result;
    }

private:
    void init_hann_window() {
        window_energy_sum_ = 0.0f;
        for (size_t i = 0; i < window_size_; ++i) {
            window_coeffs_[i] = 0.5f * (1.0f - std::cos(2.0f * std::numbers::pi_v<float> * static_cast<float>(i) 
                                                        / static_cast<float>(window_size_ - 1)));
            window_energy_sum_ += window_coeffs_[i] * window_coeffs_[i];
        }
    }

    [[nodiscard]] std::optional<PeakInfo> extract_peak(std::span<const float> psd, 
                                                       float min_freq_hz, 
                                                       float max_freq_hz) const {
        const size_t min_bin = static_cast<size_t>(std::lround((min_freq_hz * window_size_) / sample_rate_));
        const size_t max_bin = static_cast<size_t>(std::lround((max_freq_hz * window_size_) / sample_rate_));

        if (min_bin >= psd.size() || max_bin >= psd.size() || min_bin >= max_bin) {
            return std::nullopt;
        }

        auto max_it = std::max_element(psd.begin() + min_bin, psd.begin() + max_bin + 1);
        const size_t max_bin_idx = std::distance(psd.begin(), max_it);

        if (max_bin_idx <= min_bin || max_bin_idx >= max_bin) {
            return std::nullopt;
        }

        // Квадратична субпіксельна інтерполяція максимуму
        const float alpha = psd[max_bin_idx - 1];
        const float beta  = psd[max_bin_idx];
        const float gamma = psd[max_bin_idx + 1];
        const float delta = 0.5f * (alpha - gamma) / (alpha - 2.0f * beta + gamma);

        PeakInfo peak;
        peak.frequency_hz  = ((static_cast<float>(max_bin_idx) + delta) * sample_rate_) / static_cast<float>(window_size_);
        peak.amplitude_psd = beta - 0.25f * (alpha - gamma) * delta;
        
        constexpr float bin_width_hz = 0.25f;
        peak.quality_factor = peak.frequency_hz / (2.0f * bin_width_hz);

        return peak;
    }

    size_t window_size_;
    float sample_rate_;
    float window_energy_sum_{0.0f};
    std::vector<float> window_coeffs_;
};

} // namespace dsp::schumann
