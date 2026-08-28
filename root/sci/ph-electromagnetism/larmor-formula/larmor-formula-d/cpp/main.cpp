#include <iostream>
#include <iomanip>
#include <cmath>
#include <vector>
#include <numbers>

namespace electrodynamics {

constexpr double C_LIGHT = 2.99792458e8;     // м/с
constexpr double EPS0    = 8.8541878128e-12; // Ф/м
constexpr double Q_ELEM  = 1.602176634e-19; // Кл
constexpr double M_ELEM  = 9.1093837015e-31; // кг

[[nodiscard]] double calculate_larmor_power(double ax, double ay, double az) noexcept {
    const double a_sq = ax * ax + ay * ay + az * az;
    return (Q_ELEM * Q_ELEM * a_sq) /
           (6.0 * std::numbers::pi * EPS0 * C_LIGHT * C_LIGHT * C_LIGHT);
}

} // namespace electrodynamics

int main() {
    using namespace electrodynamics;

    constexpr double E0    = 1.0e6;           // 1 МВ/м
    constexpr double FREQ  = 5.0e14;          // 500 ТГц (видиме світло)
    constexpr double OMEGA = 2.0 * std::numbers::pi * FREQ;
    constexpr double DT    = 1.0e-17;         // 10 аттосекунд
    constexpr int STEPS    = 1000;

    double current_time = 0.0;
    double total_energy = 0.0;

    std::cout << std::left
              << std::setw(10) << "Час (фс)"
              << std::setw(14) << "Поле (кВ/м)"
              << std::setw(28) << "Прискорення (10^17 м/с^2)"
              << "Потужність (пВт)\n";
    std::cout << std::string(68, '-') << "\n";

    for (int i = 0; i <= STEPS; ++i) {
        const double e_field = E0 * std::sin(OMEGA * current_time);
        const double a_x = (-Q_ELEM * e_field) / M_ELEM;
        const double p_rad = calculate_larmor_power(a_x, 0.0, 0.0);

        total_energy += p_rad * DT;

        if (i % 200 == 0) {
            std::cout << std::left
                      << std::fixed << std::setprecision(3)
                      << std::setw(10) << (current_time * 1.0e15)
                      << std::setprecision(2)
                      << std::setw(14) << (e_field * 1.0e-3)
                      << std::setprecision(4)
                      << std::setw(28) << (a_x * 1.0e-17)
                      << std::scientific << std::setprecision(4)
                      << (p_rad * 1.0e12) << "\n";
        }
        current_time += DT;
    }

    std::cout << "\nПовна випромінена енергія за розрахунковий інтервал: "
              << std::scientific << std::setprecision(6) << total_energy << " Дж\n";

    return 0;
}
