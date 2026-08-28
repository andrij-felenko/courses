// Steinmetz Core Loss Calculator (C++20 implementation)
#include <iostream>
#include <vector>
#include <span>
#include <cmath>
#include <numbers>
#include <algorithm>
#include <format>

struct SteinmetzParams {
    double k{16.9};     // Material constant k
    double alpha{1.25}; // Frequency exponent
    double beta{2.55};  // Flux density exponent

    [[nodiscard]] double calculate_k_i() const noexcept {
        const double term1 = std::pow(2.0 * std::numbers::pi, alpha - 1.0);
        const double term2 = std::pow(2.0, beta - alpha + 1.0);
        const double beta_val = (std::tgamma((alpha + 1.0) / 2.0) * std::tgamma(0.5)) / 
                                 std::tgamma(alpha / 2.0 + 1.0);
        return k / (term1 * term2 * beta_val);
    }
};

class CoreLossCalculator {
public:
    explicit CoreLossCalculator(SteinmetzParams params) : params_(params) {}

    // Calculate OSE loss density (W/m^3) for pure sine wave
    [[nodiscard]] double calculate_ose(double freq_hz, double b_peak_tesla) const noexcept {
        return params_.k * std::pow(freq_hz, params_.alpha) * std::pow(b_peak_tesla, params_.beta);
    }

    // Calculate iSE loss density (W/m^3) for discrete B(t) sample span
    [[nodiscard]] double calculate_ise(std::span<const double> b_samples, double period_sec) const {
        if (b_samples.size() < 2 || period_sec <= 0.0) {
            return 0.0;
        }

        const double dt = period_sec / static_cast<double>(b_samples.size() - 1);
        const auto [min_it, max_it] = std::minmax_element(b_samples.begin(), b_samples.end());
        const double delta_b = *max_it - *min_it;
        if (delta_b <= 0.0) return 0.0;

        const double k_i = params_.calculate_k_i();
        double integral_sum = 0.0;

        for (size_t i = 0; i < b_samples.size() - 1; ++i) {
            const double db_dt = (b_samples[i + 1] - b_samples[i]) / dt;
            integral_sum += std::pow(std::abs(db_dt), params_.alpha) * dt;
        }

        const double avg_integral = integral_sum / period_sec;
        return k_i * avg_integral * std::pow(delta_b, params_.beta - params_.alpha);
    }

private:
    SteinmetzParams params_;
};

int main() {
    SteinmetzParams n87_ferrite{.k = 16.9, .alpha = 1.25, .beta = 2.55};
    CoreLossCalculator calc(n87_ferrite);

    constexpr double freq = 100'000.0; // 100 kHz
    constexpr double b_peak = 0.1;     // 100 mT

    const double ose_loss = calc.calculate_ose(freq, b_peak);
    std::cout << std::format("OSE Loss: {:.2f} W/m^3 ({:.2f} mW/cm^3)\n", 
                              ose_loss, ose_loss / 1000.0);

    // Generate triangular B(t) waveform for 50% duty PWM
    constexpr size_t num_pts = 1000;
    std::vector<double> b_triangular(num_pts);
    const double period = 1.0 / freq;
    for (size_t i = 0; i < num_pts; ++i) {
        double t_rel = static_cast<double>(i) / (num_pts - 1); // 0.0 to 1.0
        if (t_rel < 0.5) {
            b_triangular[i] = -b_peak + 4.0 * b_peak * t_rel;
        } else {
            b_triangular[i] = b_peak - 4.0 * b_peak * (t_rel - 0.5);
        }
    }

    const double ise_loss = calc.calculate_ise(b_triangular, period);
    std::cout << std::format("iSE Loss (PWM Triangle): {:.2f} W/m^3 ({:.2f} mW/cm^3)\n", 
                              ise_loss, ise_loss / 1000.0);

    return 0;
}
