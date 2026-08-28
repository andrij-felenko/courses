#include <iostream>
#include <vector>
#include <cmath>
#include <numbers>
#include <optional>
#include <string_view>
#include <iomanip>

namespace physics::nonlinear {

struct CircleMapConfig {
    double omega{0.0};
    double k{0.0};
    std::size_t transient_steps{10000};
    std::size_t measure_steps{50000};
    double initial_x{0.0};
};

struct ResonanceInfo {
    int numerator{0};
    int denominator{1};
    double error{0.0};
};

struct SimulationResult {
    double rotation_number{0.0};
    std::optional<ResonanceInfo> resonance{};
};

class CircleMapSimulator {
public:
    explicit constexpr CircleMapSimulator(CircleMapConfig config) noexcept
        : config_{config} {}

    [[nodiscard]] SimulationResult run(int max_denominator = 16, double tolerance = 1e-4) const {
        double x = config_.initial_x;
        const double two_pi = 2.0 * std::numbers::pi;

        // 1. Пропускаємо перехідний процес
        for (std::size_t i = 0; i < config_.transient_steps; ++i) {
            x = step(x, two_pi);
        }

        // 2. Вимірюємо точний зсув фази
        const double start_x = x;
        for (std::size_t i = 0; i < config_.measure_steps; ++i) {
            x = step(x, two_pi);
        }

        const double delta_x = x - start_x;
        const double rot_num = delta_x / static_cast<double>(config_.measure_steps);

        // 3. Шукаємо найближчий резонансний дріб
        SimulationResult result;
        result.rotation_number = rot_num;
        result.resonance = detect_resonance(rot_num, max_denominator, tolerance);

        return result;
    }

private:
    [[nodiscard]] constexpr double step(double x, double two_pi) const noexcept {
        return x + config_.omega - (config_.k / two_pi) * std::sin(two_pi * x);
    }

    [[nodiscard]] static std::optional<ResonanceInfo> detect_resonance(
        double w, int max_q, double tol) noexcept 
    {
        const double norm_w = w - std::floor(w);
        int best_p = 0;
        int best_q = 1;
        double min_diff = std::abs(norm_w);

        for (int q = 1; q <= max_q; ++q) {
            const int p = static_cast<int>(std::round(norm_w * static_cast<double>(q)));
            const double diff = std::abs(norm_w - static_cast<double>(p) / static_cast<double>(q));
            if (diff < min_diff) {
                min_diff = diff;
                best_p = p;
                best_q = q;
            }
        }

        if (min_diff <= tol) {
            return ResonanceInfo{.numerator = best_p, .denominator = best_q, .error = min_diff};
        }
        return std::nullopt;
    }

    CircleMapConfig config_;
};

} // namespace physics::nonlinear

int main() {
    using namespace physics::nonlinear;

    const CircleMapConfig config{
        .omega = 0.33333333,
        .k = 0.8,
        .transient_steps = 10000,
        .measure_steps = 50000,
        .initial_x = 0.1
    };

    const CircleMapSimulator simulator{config};
    const auto result = simulator.run(16, 1e-4);

    std::cout << std::fixed << std::setprecision(6);
    std::cout << "Параметри: Omega = " << config.omega << ", K = " << config.k << "\n";
    std::cout << "Число обертання W = " << result.rotation_number << "\n";

    if (result.resonance) {
        std::cout << "Стан: Фазове захоплення на резонансі "
                  << result.resonance->numerator << "/" << result.resonance->denominator
                  << " (абсолютна похибка: " << result.resonance->error << ")\n";
    } else {
        std::cout << "Стан: Квазіперіодичний рух (поза язиками)\n";
    }

    return 0;
}
