#include <iostream>
#include <vector>
#include <cmath>
#include <numbers>
#include <iomanip>
#include <span>
#include <memory>

namespace qhe {

// Фундаментальні фізичні константи у системі SI
constexpr double h_Planck = 6.62607015e-34;     // Дж·с
constexpr double e_charge = 1.602176634e-19;    // Кл
constexpr double k_Boltzmann = 1.380649e-23;    // Дж/К
constexpr double m_electron = 9.1093837015e-31; // кг

// Параметри напівпровідникового зразка 2DEG
struct SampleParameters {
    double electron_density{3.2e15}; // м^-2
    double effective_mass{0.067};   // m* / m_e
    double temperature{1.2};         // Кельвіни
    double mobility{60.0};           // м^2 / (В·с)
};

// Результат чисельного розрахунку у точці
struct TransportDataPoint {
    double magnetic_field{};
    double filling_factor{};
    int plateau_index{};
    double r_hall{};
    double r_longitudinal{};
};

// Симулятор квантового транспорту Холла
class HallSimulator {
public:
    explicit HallSimulator(SampleParameters params) noexcept
        : params_(params) {}

    [[nodiscard]] TransportDataPoint compute_at(double B) const noexcept {
        TransportDataPoint pt;
        pt.magnetic_field = B;

        const double n_B = (e_charge * B) / h_Planck;
        pt.filling_factor = params_.electron_density / n_B;

        const int i_near = std::max(1, static_cast<int>(std::round(pt.filling_factor)));
        pt.plateau_index = i_near;

        const double deviation = std::abs(pt.filling_factor - static_cast<double>(i_near));
        constexpr double plateau_threshold = 0.15;

        if (deviation < plateau_threshold) {
            // Режим квантованого плато
            pt.r_hall = h_Planck / (static_cast<double>(i_near) * e_charge * e_charge);

            const double m_kg = params_.effective_mass * m_electron;
            const double hbar = h_Planck / (2.0 * std::numbers::pi);
            const double hw_c = (hbar * e_charge * B) / m_kg;
            const double thermal_suppression = std::exp(-hw_c / (2.0 * k_Boltzmann * params_.temperature));
            pt.r_longitudinal = 500.0 * thermal_suppression;
        } else {
            // Режим міжплатоного переходу
            pt.r_hall = h_Planck / (pt.filling_factor * e_charge * e_charge);
            const double peak_shape = std::sin(std::numbers::pi * pt.filling_factor);
            pt.r_longitudinal = 1500.0 * (peak_shape * peak_shape);
        }

        return pt;
    }

    [[nodiscard]] std::vector<TransportDataPoint> sweep(double b_min, double b_max, std::size_t steps) const {
        if (steps < 2) return {};

        std::vector<TransportDataPoint> results;
        results.reserve(steps);

        const double dB = (b_max - b_min) / static_cast<double>(steps - 1);
        for (std::size_t k = 0; k < steps; ++k) {
            results.push_back(compute_at(b_min + static_cast<double>(k) * dB));
        }

        return results;
    }

private:
    SampleParameters params_;
};

// Функція виводу звіту з використанням C++ std::span для безпечного доступу до пам'яті
void print_simulation_report(std::span<const TransportDataPoint> data) {
    std::cout << "===================================================================\n";
    std::cout << "  СИМУЛЯЦІЯ ТРАНСПОРТУ QHE В ДВОВИМІРНОМУ ЕЛЕКТРОННОМУ ГАЗІ (C++20)\n";
    std::cout << "===================================================================\n";
    std::cout << std::setw(8) << "B (Тл)" << " | "
              << std::setw(9) << "Factor nu" << " | "
              << std::setw(7) << "Index i" << " | "
              << std::setw(14) << "R_xy (Ом)" << " | "
              << std::setw(13) << "R_xx (Ом)" << "\n";
    std::cout << "-------------------------------------------------------------------\n";

    for (const auto& point : data) {
        std::cout << std::fixed << std::setprecision(2)
                  << std::setw(8) << point.magnetic_field << " | "
                  << std::setprecision(3)
                  << std::setw(9) << point.filling_factor << " | "
                  << std::setw(7) << point.plateau_index << " | "
                  << std::setprecision(4)
                  << std::setw(14) << point.r_hall << " | "
                  << std::setprecision(5)
                  << std::setw(13) << point.r_longitudinal << "\n";
    }

    std::cout << "-------------------------------------------------------------------\n";
}

} // namespace qhe

int main() {
    qhe::SampleParameters gaas_params{
        .electron_density = 3.2e15,
        .effective_mass = 0.067,
        .temperature = 1.2,
        .mobility = 60.0
    };

    const qhe::HallSimulator simulator(gaas_params);
    const auto results = simulator.sweep(1.0, 8.5, 16);

    qhe::print_simulation_report(results);

    return 0;
}
