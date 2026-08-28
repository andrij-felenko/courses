#include <iostream>
#include <vector>
#include <cmath>
#include <numbers>
#include <iomanip>
#include <string>

struct DoubleSlitParams {
    double wavelength{632.8e-9}; // Довжина хвилі λ (м)
    double d{0.2e-3};            // Відстань між щілинами d (м)
    double a{0.04e-3};           // Ширина щілини a (м)
    double L{2.0};               // Відстань до екрана L (м)
    double gamma{1.0};           // Ступінь когерентності [0.0..1.0]
};

class DoubleSlitSimulator {
public:
    explicit DoubleSlitSimulator(DoubleSlitParams params)
        : params_(params) {}

    [[nodiscard]] double compute_intensity(double y) const noexcept {
        if (params_.L <= 0.0 || params_.wavelength <= 0.0) return 0.0;

        const double sin_theta = y / std::sqrt(y * y + params_.L * params_.L);
        const double alpha = (std::numbers::pi * params_.d * sin_theta) / params_.wavelength;
        const double beta  = (std::numbers::pi * params_.a * sin_theta) / params_.wavelength;

        const double interference = 1.0 + params_.gamma * std::cos(2.0 * alpha);

        double diffraction = 1.0;
        if (std::abs(beta) > 1e-7) {
            const double sinc = std::sin(beta) / beta;
            diffraction = sinc * sinc;
        } else {
            diffraction = 1.0 - (beta * beta) / 3.0;
        }

        return interference * diffraction;
    }

    [[nodiscard]] std::vector<double> generate_profile(double y_max, size_t steps) const {
        std::vector<double> profile;
        profile.reserve(steps);

        const double dy = (2.0 * y_max) / static_cast<double>(steps - 1);
        for (size_t i = 0; i < steps; ++i) {
            const double y = -y_max + static_cast<double>(i) * dy;
            profile.push_back(compute_intensity(y));
        }
        return profile;
    }

    void render_ascii(double y_max, size_t steps, size_t max_bars = 40) const {
        std::cout << "=== Двощілинна інтерференція (C++) ===\n";
        std::cout << "Параметри: λ = " << params_.wavelength * 1e9 << " нм, d = "
                  << params_.d * 1e3 << " мм, a = " << params_.a * 1e3
                  << " мм, L = " << params_.L << " м, γ = " << params_.gamma << "\n\n";

        const double dy = (2.0 * y_max) / static_cast<double>(steps - 1);
        for (size_t i = 0; i < steps; ++i) {
            const double y = -y_max + static_cast<double>(i) * dy;
            const double intensity = compute_intensity(y);

            const auto stars = static_cast<size_t>(intensity * (max_bars / 2.0));
            std::cout << std::setw(7) << std::fixed << std::setprecision(2) << y * 1e3 << " мм | "
                      << std::string(stars, '*') << " (" << std::setprecision(3) << intensity << ")\n";
        }
    }

private:
    DoubleSlitParams params_;
};

int main() {
    const DoubleSlitParams params{
        .wavelength = 632.8e-9,
        .d = 0.2e-3,
        .a = 0.04e-3,
        .L = 2.0,
        .gamma = 1.0
    };

    const DoubleSlitSimulator sim(params);
    sim.render_ascii(0.015, 21, 40);

    return 0;
}
