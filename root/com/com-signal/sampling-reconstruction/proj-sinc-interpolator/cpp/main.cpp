#include <iostream>
#include <vector>
#include <cmath>
#include <numbers>
#include <span>
#include <stdexcept>
#include <algorithm>

class SignalReconstructor {
public:
    enum class Method {
        ZeroOrderHold,
        Linear,
        WindowedSincLanczos
    };

    explicit SignalReconstructor(std::vector<double> samples, double sample_rate)
        : m_samples(std::move(samples)), m_sample_rate(sample_rate) {
        if (m_sample_rate <= 0.0) {
            throw std::invalid_argument("Sample rate must be positive");
        }
    }

    [[nodiscard]] double reconstruct_at(double t, Method method = Method::WindowedSincLanczos, int sinc_radius = 4) const {
        if (m_samples.empty()) return 0.0;

        switch (method) {
            case Method::ZeroOrderHold:
                return interpolate_zoh(t);
            case Method::Linear:
                return interpolate_linear(t);
            case Method::WindowedSincLanczos:
                return interpolate_sinc_lanczos(t, sinc_radius);
        }
        return 0.0;
    }

private:
    std::vector<double> m_samples;
    double m_sample_rate;

    [[nodiscard]] static constexpr double sinc(double x) noexcept {
        if (std::abs(x) < 1e-9) return 1.0;
        const double px = std::numbers::pi * x;
        return std::sin(px) / px;
    }

    [[nodiscard]] static double lanczos_kernel(double x, int a) noexcept {
        if (std::abs(x) >= static_cast<double>(a)) return 0.0;
        return sinc(x) * sinc(x / static_cast<double>(a));
    }

    [[nodiscard]] double interpolate_zoh(double t) const noexcept {
        if (t <= 0.0) return m_samples.front();
        const double sample_pos = t * m_sample_rate;
        const auto idx = static_cast<std::size_t>(std::floor(sample_pos));
        if (idx >= m_samples.size()) return m_samples.back();
        return m_samples[idx];
    }

    [[nodiscard]] double interpolate_linear(double t) const noexcept {
        if (t <= 0.0) return m_samples.front();
        const double sample_pos = t * m_sample_rate;
        const auto idx0 = static_cast<std::size_t>(std::floor(sample_pos));
        const std::size_t idx1 = idx0 + 1;

        if (idx1 >= m_samples.size()) return m_samples.back();

        const double frac = sample_pos - static_cast<double>(idx0);
        return (1.0 - frac) * m_samples[idx0] + frac * m_samples[idx1];
    }

    [[nodiscard]] double interpolate_sinc_lanczos(double t, int radius) const noexcept {
        const double sample_pos = t * m_sample_rate;
        const auto center_idx = static_cast<std::ptrdiff_t>(std::floor(sample_pos));
        const auto n_samples = static_cast<std::ptrdiff_t>(m_samples.size());

        double sum = 0.0;
        double weight_sum = 0.0;

        for (std::ptrdiff_t i = center_idx - radius + 1; i <= center_idx + radius; ++i) {
            if (i >= 0 && i < n_samples) {
                const double dx = sample_pos - static_cast<double>(i);
                const double w = lanczos_kernel(dx, radius);
                sum += m_samples[static_cast<std::size_t>(i)] * w;
                weight_sum += w;
            }
        }

        return (weight_sum > 1e-9) ? (sum / weight_sum) : 0.0;
    }
};

int main() {
    constexpr double fs = 20.0;
    constexpr std::size_t num_samples = 40;
    std::vector<double> samples(num_samples);

    for (std::size_t i = 0; i < num_samples; ++i) {
        const double t = static_cast<double>(i) / fs;
        samples[i] = std::sin(2.0 * std::numbers::pi * 2.0 * t) + 0.5 * std::sin(2.0 * std::numbers::pi * 5.0 * t);
    }

    SignalReconstructor reconstructor(std::move(samples), fs);

    constexpr double test_t = 0.355;
    const double true_val = std::sin(2.0 * std::numbers::pi * 2.0 * test_t) + 0.5 * std::sin(2.0 * std::numbers::pi * 5.0 * test_t);

    std::cout << "--- C++ Signal Reconstruction Test at t = " << test_t << " s ---
";
    std::cout << "True value:      " << true_val << "
";
    std::cout << "ZOH value:       " << reconstructor.reconstruct_at(test_t, SignalReconstructor::Method::ZeroOrderHold) << "
";
    std::cout << "Linear value:    " << reconstructor.reconstruct_at(test_t, SignalReconstructor::Method::Linear) << "
";
    std::cout << "Sinc (Lanczos4): " << reconstructor.reconstruct_at(test_t, SignalReconstructor::Method::WindowedSincLanczos, 4) << "
";

    return 0;
}
