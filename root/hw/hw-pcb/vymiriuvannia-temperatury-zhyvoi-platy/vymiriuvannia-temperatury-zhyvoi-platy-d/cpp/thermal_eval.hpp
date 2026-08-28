/**
 * @file thermal_eval.hpp
 * @brief Ідіоматична перевірка теплових меж напівпровідника за JESD51 на C++20.
 */

#pragma once

#include <iostream>
#include <expected>
#include <string_view>
#include <format>

namespace pcb_thermal {

struct ThermalParameters {
    float t_case_measured_c{25.0f};
    float power_dissipated_w{0.0f};
    float psi_jt{1.5f};             ///< JEDEC Psi-JT (°C/Вт)
    float t_junction_max_c{150.0f}; ///< T_J(max) з datasheet
    float safety_margin_c{20.0f};   ///< Інженерний запас надійності
};

struct ThermalAssessment {
    float junction_temp_c{0.0f};
    float headroom_c{0.0f};
    bool is_compliant{false};
};

enum class ThermalViolation {
    CriticalOvertemp,
    InsufficientMargin
};

[[nodiscard]] constexpr std::expected<ThermalAssessment, ThermalViolation>
evaluate_component_thermal_state(const ThermalParameters& params) noexcept {
    const float t_j = params.t_case_measured_c + (params.psi_jt * params.power_dissipated_w);
    const float margin = params.t_junction_max_c - t_j;

    if (margin < 0.0f) {
        return std::unexpected(ThermalViolation::CriticalOvertemp);
    }
    if (margin < params.safety_margin_c) {
        return std::unexpected(ThermalViolation::InsufficientMargin);
    }

    return ThermalAssessment{
        .junction_temp_c = t_j,
        .headroom_c = margin,
        .is_compliant = true
    };
}

} // namespace pcb_thermal
