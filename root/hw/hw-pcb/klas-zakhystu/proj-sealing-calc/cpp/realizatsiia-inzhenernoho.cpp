#include <iostream>
#include <cmath>
#include <numbers>
#include <expected>
#include <string_view>
#include <format>

namespace sealing {

enum class CalculationError {
    InvalidGeometry,
    InvalidHardness,
    InvalidTemperature,
    ZeroTimeInterval
};

struct GasketParameters {
    double cord_diameter_mm{2.5};      // Діаметр шнура d_s
    double gland_width_mm{3.4};        // Ширина паза W
    double gland_depth_mm{1.9};        // Глибина паза H
    double perimeter_mm{500.0};        // Повний периметр ущільнення
    double bolt_spacing_mm{45.0};      // Відстань між гвинтами
    double flange_thickness_mm{3.0};   // Товщина фланця
    double flange_width_mm{8.0};       // Ширина фланця
    double shore_a{70.0};              // Твердість за Шором А
    double mat_young_modulus_mpa{70000.0}; // Модуль Юнга матеріалу (Алюміній)
    double internal_volume_l{1.2};     // Внутрішній об'єм корпусу
    double temp_hot_c{65.0};           // Робоча температура
    double temp_cold_c{10.0};          // Температура охолодження
    double target_time_sec{60.0};      // Час вирівнювання тиску
    double vent_permeability{400.0};   // Проникність ePTFE (мл/хв*см^2 при 7 кПа)
};

struct GasketAnalysis {
    double compression_pct{0.0};
    double gland_fill_pct{0.0};
    double elastomer_modulus_mpa{0.0};
    double linear_force_n_per_mm{0.0};
    double total_force_n{0.0};
    double bolt_force_n{0.0};
    double flange_deflection_mm{0.0};
    double max_allowed_deflection_mm{0.0};
    double thermal_vacuum_kpa{0.0};
    double airflow_req_ml_min{0.0};
    double min_vent_area_cm2{0.0};
    
    [[nodiscard]] constexpr bool is_compression_valid() const noexcept {
        return compression_pct >= 18.0 && compression_pct <= 32.0;
    }
    
    [[nodiscard]] constexpr bool is_fill_valid() const noexcept {
        return gland_fill_pct >= 65.0 && gland_fill_pct <= 85.0;
    }
    
    [[nodiscard]] constexpr bool is_deflection_valid() const noexcept {
        return flange_deflection_mm <= max_allowed_deflection_mm;
    }
    
    [[nodiscard]] constexpr bool is_pass() const noexcept {
        return is_compression_valid() && is_fill_valid() && is_deflection_valid();
    }
};

class EnclosureSealingCalculator {
public:
    [[nodiscard]] static std::expected<GasketAnalysis, CalculationError> calculate(const GasketParameters& p) noexcept {
        if (p.cord_diameter_mm <= 0.0 || p.gland_width_mm <= 0.0 || p.gland_depth_mm <= 0.0 ||
            p.gland_depth_mm >= p.cord_diameter_mm) {
            return std::unexpected(CalculationError::InvalidGeometry);
        }
        if (p.shore_a <= 10.0 || p.shore_a >= 95.0) {
            return std::unexpected(CalculationError::InvalidHardness);
        }
        if (p.target_time_sec <= 0.0 || p.vent_permeability <= 0.0) {
            return std::unexpected(CalculationError::ZeroTimeInterval);
        }

        GasketAnalysis res{};

        // 1. Стиснення та заповнення паза
        res.compression_pct = ((p.cord_diameter_mm - p.gland_depth_mm) / p.cord_diameter_mm) * 100.0;
        
        const double a_seal = (std::numbers::pi * p.cord_diameter_mm * p.cord_diameter_mm) / 4.0;
        const double a_gland = p.gland_width_mm * p.gland_depth_mm;
        res.gland_fill_pct = (a_seal / a_gland) * 100.0;

        // 2. Модуль пружності та контактне навантаження
        res.elastomer_modulus_mpa = (15.75 + 2.15 * p.shore_a) / (100.0 - p.shore_a);
        
        const double c_frac = std::max(0.0, res.compression_pct / 100.0);
        res.linear_force_n_per_mm = res.elastomer_modulus_mpa * p.cord_diameter_mm *
            (1.25 * std::pow(c_frac, 1.5) + 0.1 * std::pow(c_frac, 3.0));
        
        res.total_force_n = res.linear_force_n_per_mm * p.perimeter_mm;
        
        const double num_bolts = std::max(1.0, p.perimeter_mm / p.bolt_spacing_mm);
        res.bolt_force_n = res.total_force_n / num_bolts;

        // 3. Прогин фланця
        const double i_flange = (p.flange_width_mm * std::pow(p.flange_thickness_mm, 3.0)) / 12.0;
        res.flange_deflection_mm = (res.linear_force_n_per_mm * std::pow(p.bolt_spacing_mm, 4.0)) /
            (384.0 * p.mat_young_modulus_mpa * i_flange);
        res.max_allowed_deflection_mm = 0.05 * p.cord_diameter_mm;

        // 4. Термічний вакуум і повітрообмін мембрани
        const double t_hot_k = p.temp_hot_c + 273.15;
        const double t_cold_k = p.temp_cold_c + 273.15;
        constexpr double p_atm_kpa = 101.325;

        if (t_hot_k > t_cold_k) {
            res.thermal_vacuum_kpa = p_atm_kpa * (1.0 - (t_cold_k / t_hot_k));
        } else {
            res.thermal_vacuum_kpa = 0.0;
        }

        const double tau_min = p.target_time_sec / 60.0;
        res.airflow_req_ml_min = (p.internal_volume_l * 1000.0 * (res.thermal_vacuum_kpa / p_atm_kpa)) / tau_min;
        
        const double delta_p_norm = std::max(0.1, res.thermal_vacuum_kpa / 7.0);
        res.min_vent_area_cm2 = res.airflow_req_ml_min / (p.vent_permeability * delta_p_norm);

        return res;
    }
};

} // namespace sealing
