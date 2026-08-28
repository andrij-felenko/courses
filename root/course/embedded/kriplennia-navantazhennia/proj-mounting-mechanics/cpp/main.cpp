// mounting_validator.hpp / .cpp — Ідіоматичний C++20 модуль верифікації кріплення
#include <iostream>
#include <cmath>
#include <numbers>
#include <algorithm>
#include <format>
#include <expected>
#include <span>

namespace drone::mounting {

// ── Сильно типізовані конфігураційні структури ─────────────────────────────

struct BoltSpecs {
    float yield_strength_mpa{900.0f}; // Клас 10.9: 900 МПа
    float core_area_mm2{5.03f};       // M3 = 5.03 мм²
    int   bolt_count{4};
};

struct PayloadSpecs {
    float mass_kg{0.650f};
    float power_watts{22.0f};
    float max_junction_temp_c{100.0f};
    float r_th_jc{0.8f};             // °C/Вт
    float r_th_cs{0.4f};             // °C/Вт
    float heatsink_area_m2{0.024f};  // 240 см²
};

struct DamperSpecs {
    float single_stiffness_n_per_m{3500.0f};
    int   damper_count{4};
    float damping_ratio_zeta{0.24f};
};

struct FlightEnvironment {
    float rpm_min{4500.0f};
    float rpm_max{8200.0f};
    int   blade_count{2};
    float g_maneuver{4.0f};
    float g_impact{12.0f};
    float ambient_temp_c{35.0f};
    float airspeed_m_s{15.0f};
};

struct ValidationSummary {
    float bolt_von_mises_mpa;
    float bolt_safety_factor;
    bool  bolt_passed;

    float natural_frequency_hz;
    float transmissibility_min_rpm;
    bool  vibration_passed;

    float total_thermal_resistance;
    float predicted_junction_temp_c;
    bool  thermal_passed;

    [[nodiscard]] constexpr bool is_fully_valid() const noexcept {
        return bolt_passed && vibration_passed && thermal_passed;
    }
};

enum class FailureReason {
    InvalidMass,
    ZeroBolts,
    ExcessiveStress,
    ResonanceRisk,
    ThermalOverheat
};

// ── Клас верифікатора надійності ───────────────────────────────────────────

class MountingValidator {
public:
    static std::expected<ValidationSummary, FailureReason> validate(
        const PayloadSpecs& payload,
        const BoltSpecs& bolts,
        const DamperSpecs& dampers,
        const FlightEnvironment& env
    ) noexcept {
        if (payload.mass_kg <= 0.0f) {
            return std::unexpected(FailureReason::InvalidMass);
        }
        if (bolts.bolt_count <= 0) {
            return std::unexpected(FailureReason::ZeroBolts);
        }

        constexpr float g_acc = 9.80665f;
        ValidationSummary summary{};

        // 1. Аналіз болтів (Von Mises)
        const float total_impact_force = payload.mass_kg * env.g_impact * g_acc;
        const float force_per_bolt = total_impact_force / static_cast<float>(bolts.bolt_count);

        const float shear_stress = (force_per_bolt * 0.7071f) / bolts.core_area_mm2;
        const float tensile_stress = (force_per_bolt * 0.7071f) / bolts.core_area_mm2;

        summary.bolt_von_mises_mpa = std::sqrt(
            tensile_stress * tensile_stress + 3.0f * shear_stress * shear_stress
        );
        summary.bolt_safety_factor = bolts.yield_strength_mpa / summary.bolt_von_mises_mpa;
        summary.bolt_passed = (summary.bolt_safety_factor >= 1.50f);

        // 2. Аналіз віброізоляції
        const float total_k = dampers.single_stiffness_n_per_m * static_cast<float>(dampers.damper_count);
        summary.natural_frequency_hz = (1.0f / (2.0f * std::numbers::pi_v<float>)) *
                                       std::sqrt(total_k / payload.mass_kg);

        const float f_rot_min = env.rpm_min / 60.0f;
        const float r = f_rot_min / summary.natural_frequency_hz;
        const float z = dampers.damping_ratio_zeta;

        const float tr_num = 1.0f + std::pow(2.0f * z * r, 2.0f);
        const float tr_den = std::pow(1.0f - r * r, 2.0f) + std::pow(2.0f * z * r, 2.0f);
        summary.transmissibility_min_rpm = std::sqrt(tr_num / tr_den);

        summary.vibration_passed = (summary.natural_frequency_hz * 1.4142f < f_rot_min) &&
                                   (summary.transmissibility_min_rpm <= 0.25f);

        // 3. Аналіз теплового режиму
        const float airspeed = std::max(env.airspeed_m_s, 0.0f);
        const float h_conv = 10.0f + 6.5f * std::pow(airspeed, 0.8f);
        const float r_th_sa = 1.0f / (h_conv * payload.heatsink_area_m2);

        summary.total_thermal_resistance = payload.r_th_jc + payload.r_th_cs + r_th_sa;
        summary.predicted_junction_temp_c = env.ambient_temp_c +
                                            payload.power_watts * summary.total_thermal_resistance;
        summary.thermal_passed = (summary.predicted_junction_temp_c <= payload.max_junction_temp_c - 10.0f);

        return summary;
    }
};

} // namespace drone::mounting

int main() {
    using namespace drone::mounting;

    PayloadSpecs payload{};
    BoltSpecs bolts{};
    DamperSpecs dampers{};
    FlightEnvironment env{};

    auto result = MountingValidator::validate(payload, bolts, dampers, env);

    if (!result) {
        std::cerr << "Помилка валідації параметрів монтажу!\n";
        return 1;
    }

    const auto& res = result.value();
    std::cout << "================ C++20 МОНТАЖНИЙ АНАЛІЗАТОР ================\n";
    std::cout << std::format("Болти: напруження {:.1f} МПа, Запас: {:.2f} [{}]\n",
                             res.bolt_von_mises_mpa, res.bolt_safety_factor,
                             res.bolt_passed ? "OK" : "FAIL");
    std::cout << std::format("Віброізоляція: f_0 = {:.2f} Гц, T_R = {:.3f} [{}]\n",
                             res.natural_frequency_hz, res.transmissibility_min_rpm,
                             res.vibration_passed ? "OK" : "FAIL");
    std::cout << std::format("Тепло: T_j = {:.1f} °C, R_th = {:.2f} °C/Вт [{}]\n",
                             res.predicted_junction_temp_c, res.total_thermal_resistance,
                             res.thermal_passed ? "OK" : "FAIL");
    std::cout << std::format("Загальний статус допуску до польоту: {}\n",
                             res.is_fully_valid() ? "СХВАЛЕНО" : "ЗАБЛОКОВАНО");
    std::cout << "=============================================================\n";

    return 0;
}
