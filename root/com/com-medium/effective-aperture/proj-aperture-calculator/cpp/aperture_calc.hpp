// aperture_calc.hpp — Сучасний ідіоматичний модуль на C++20 / C++23
#ifndef APERTURE_CALC_HPP
#define APERTURE_CALC_HPP

#include <cmath>
#include <numbers>
#include <expected>
#include <span>
#include <vector>
#include <iostream>
#include <format>

namespace rf {

constexpr double speed_of_light = 299'792'458.0; // швидкість світла, м/с

struct AntennaParams {
    double frequency_hz{0.0};
    double gain_dbi{0.0};
    double efficiency{0.60}; // типова ефективність 60%
};

struct ApertureResult {
    double wavelength_m{0.0};
    double effective_area_m2{0.0};
    double physical_area_m2{0.0};
    double dish_diameter_m{0.0};
};

enum class ApertureError {
    InvalidFrequency,
    InvalidEfficiency
};

// Обчислення апертури з використанням std::expected (C++23)
[[nodiscard]] constexpr std::expected<ApertureResult, ApertureError>
calculate_aperture(const AntennaParams& params) noexcept {
    if (params.frequency_hz <= 0.0) {
        return std::unexpected(ApertureError::InvalidFrequency);
    }
    if (params.efficiency < 0.0 || params.efficiency > 1.0) {
        return std::unexpected(ApertureError::InvalidEfficiency);
    }

    const double lambda = speed_of_light / params.frequency_hz;
    const double g_linear = std::pow(10.0, params.gain_dbi / 10.0);

    const double a_e = (lambda * lambda / (4.0 * std::numbers::pi)) * g_linear;

    ApertureResult res{};
    res.wavelength_m = lambda;
    res.effective_area_m2 = a_e;

    if (params.efficiency > 0.0) {
        res.physical_area_m2 = a_e / params.efficiency;
        res.dish_diameter_m = std::sqrt(4.0 * res.physical_area_m2 / std::numbers::pi);
    }

    return res;
}

// Розрахунок прийнятої потужності у дБм за вхідної густини потоку S (дБВт/м²)
[[nodiscard]] constexpr double power_received_dbm(double S_dbw_m2, double a_e_m2) noexcept {
    const double a_e_db = 10.0 * std::log10(a_e_m2);
    const double p_r_dbw = S_dbw_m2 + a_e_db;
    return p_r_dbw + 30.0; // перетворення з дБВт у дБм
}

// Пакетний аналіз антенного масиву через std::span
inline void print_aperture_report(std::span<const AntennaParams> antennas) {
    size_t idx = 0;
    for (const auto& ant : antennas) {
        auto res = calculate_aperture(ant);
        if (res) {
            std::cout << std::format(
                "Антена #{}: {:.2f} ГГц, {:.1f} дБі\n"
                "  Довжина хвилі λ:   {:.2f} мм\n"
                "  Ефективна площа A_e: {:.6f} м² ({:.2f} см²)\n"
                "  Діаметр тарілки D:   {:.2f} м (при η = {:.0f}%)\n\n",
                ++idx, ant.frequency_hz / 1e9, ant.gain_dbi,
                res->wavelength_m * 1000.0,
                res->effective_area_m2, res->effective_area_m2 * 10000.0,
                res->dish_diameter_m, ant.efficiency * 100.0
            );
        }
    }
}

} // namespace rf

#endif // APERTURE_CALC_HPP
