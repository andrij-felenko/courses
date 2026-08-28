#ifndef RAYLEIGH_SCATTERING_API_HPP
#define RAYLEIGH_SCATTERING_API_HPP

#include <cstdint>
#include <vector>
#include <string>

namespace AtmosphericOptics {

/**
 * @brief Структура фізичних параметрів атмосферного шару
 */
struct AtmosphericLayerProfile {
    double altitude_km;            ///< Висота шару над рівнем моря (км)
    double pressure_hpa;           ///< Атмосферний тиск (гПа)
    double temperature_k;          ///< Температура (К)
    double molecular_density_m3;   ///< Концентрація молекул (м^-3)
    double relative_humidity_pct;  ///< Відносна вологість (%)
};

/**
 * @brief Результати спектрального розрахунку розсіяння Релея
 */
struct RayleighScatteringOutput {
    double wavelength_nm;          ///< Довжина хвилі (нм)
    double cross_section_cm2;      ///< Ефективний переріз розсіяння (см^2)
    double volume_coeff_km1;       ///< Об'ємний коефіцієнт розсіяння (км^-1)
    double optical_depth;          ///< Зенітна оптична товщина шару
    double depolarization_factor;  ///< Фактор деполяризації Кабанна F_K
};

/**
 * @brief Інтерфейс калькулятора розсіяння Релея
 */
class IRayleighCalculator {
public:
    virtual ~IRayleighCalculator() = default;

    /**
     * @brief Розрахунок профілю оптичної товщини для заданого спектрального діапазону
     * @param layers Вектор атмосферних шарів
     * @param wavelengths_nm Вектор довжин хвиль для розрахунку
     * @return Вектор розрахованих результатів для кожної довжини хвилі
     */
    [[nodiscard]] virtual std::vector<RayleighScatteringOutput> compute_profile(
        const std::vector<AtmosphericLayerProfile>& layers,
        const std::vector<double>& wavelengths_nm) const = 0;
};

} // namespace AtmosphericOptics

#endif // RAYLEIGH_SCATTERING_API_HPP
