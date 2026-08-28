// conversion_si2019.cpp — Ідіоматичний C++20 квантовий розрахунок SI-2019
#include <iostream>
#include <iomanip>
#include <numbers>

namespace si2019 {
    // Фіксовані фундаментальні константи як constexpr
    constexpr double h = 6.626'070'15e-34;  // Дж·с
    constexpr double e = 1.602'176'634e-19; // Кл

    // Квантові сталі
    constexpr double K_J = (2.0 * e) / h;    // Стала Джозефсона (Гц/В)
    constexpr double R_K = h / (e * e);      // Стала фон Клітцинга (Ом)

    // Квантова напруга Джозефсона
    [[nodiscard]] constexpr double josephson_voltage(std::size_t n_junctions, double frequency_hz) noexcept {
        return static_cast<double>(n_junctions) * frequency_hz / K_J;
    }

    // Квантовий опір Холла на плато i
    [[nodiscard]] constexpr double hall_resistance(std::size_t plateau_i) noexcept {
        return (plateau_i == 0) ? 0.0 : R_K / static_cast<double>(plateau_i);
    }
}

int main() {
    std::cout << std::setprecision(10);
    std::cout << "K_J (Josephson): " << si2019::K_J << " Hz/V\n";
    std::cout << "R_K (Klitzing):   " << si2019::R_K << " Ohm\n";

    constexpr auto v_standard = si2019::josephson_voltage(10'000, 75.0e9);
    constexpr auto r_standard = si2019::hall_resistance(2); // плато i = 2

    std::cout << "Еталонна напруга V: " << v_standard << " V\n";
    std::cout << "Еталонний опір R (i=2): " << r_standard << " Ohm\n";

    return 0;
}
