// electrostatic_sim.cpp - Чисельне моделювання індукції (Ідіоматичний C++20)
#include <iostream>
#include <cmath>
#include <vector>
#include <numbers>
#include <iomanip>
#include <concepts>

namespace electrodynamics {

template <std::floating_point T>
class InductionSimulator {
public:
    static constexpr T kEpsilon0 = static_cast<T>(8.8541878128e-12);

    struct SimulationReport {
        T analytical_charge_c;
        T numerical_charge_c;
        T error_percent;
        T force_newtons;
    };

    constexpr InductionSimulator(T charge_c, T distance_m) noexcept
        : q_(charge_c), d_(distance_m) {}

    [[nodiscard]] constexpr T surface_charge_density(T r) const noexcept {
        const T denom = std::pow(r * r + d_ * d_, static_cast<T>(1.5));
        return -(q_ * d_) / (static_cast<T>(2.0) * std::numbers::pi_v<T> * denom);
    }

    [[nodiscard]] SimulationReport compute(T r_max, std::size_t steps) const {
        const T dr = r_max / static_cast<T>(steps);
        T total_q = static_cast<T>(0.0);

        for (std::size_t i = 0; i < steps; ++i) {
            const T r1 = static_cast<T>(i) * dr;
            const T r2 = static_cast<T>(i + 1) * dr;
            const T dq1 = static_cast<T>(2.0) * std::numbers::pi_v<T> * r1 * surface_charge_density(r1);
            const T dq2 = static_cast<T>(2.0) * std::numbers::pi_v<T> * r2 * surface_charge_density(r2);
            total_q += static_cast<T>(0.5) * (dq1 + dq2) * dr;
        }

        const T k = static_cast<T>(1.0) / (static_cast<T>(4.0) * std::numbers::pi_v<T> * kEpsilon0);
        const T force = k * (q_ * q_) / (static_cast<T>(4.0) * d_ * d_);
        const T analytical = -q_;
        const T error = std::abs((total_q - analytical) / q_) * static_cast<T>(100.0);

        return {analytical, total_q, error, force};
    }

private:
    T q_;
    T d_;
};

} // namespace electrodynamics

int main() {
    using namespace electrodynamics;

    constexpr double charge = 1.0e-6;   // 1 мкКл
    constexpr double distance = 0.05;   // 5 см
    constexpr double r_max = 2.0;       // Інтегруємо до R_max = 2 м
    constexpr std::size_t steps = 50000;

    const InductionSimulator<double> sim(charge, distance);
    const auto report = sim.compute(r_max, steps);

    std::cout << std::scientific << std::setprecision(5);
    std::cout << "=== Чисельне моделювання електростатичної індукції (C++20) ===\n";
    std::cout << "Аналітичний індукований заряд: " << report.analytical_charge_c << " Кл\n";
    std::cout << "Обчислений чисельний заряд:    " << report.numerical_charge_c << " Кл\n";
    std::cout << std::fixed << std::setprecision(4);
    std::cout << "Відносна похибка інтегрування: " << report.error_percent << " %\n";
    std::cout << std::scientific << std::setprecision(5);
    std::cout << "Сила притягання до площини:    " << report.force_newtons << " Н\n";

    return 0;
}
