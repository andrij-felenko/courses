#include <iostream>
#include <cmath>
#include <numbers>
#include <expected>
#include <format>
#include <string_view>

namespace insulation {

constexpr double epsilon_0 = 8.8541878128e-12; // Ф/м

enum class calculation_error {
    invalid_geometry,
    invalid_material_properties,
    dielectric_breakdown_hazard
};

struct cable_parameters {
    double inner_radius_m;
    double outer_radius_m;
    double cable_length_m;
    double operating_voltage_v;
    double frequency_hz;
    double relative_permittivity;
    double loss_tangent;
    double breakdown_strength_v_per_m;
    double volume_resistivity_ohm_m;
};

struct calculation_results {
    double max_electric_field_v_m;
    double min_electric_field_v_m;
    double radius_ratio;
    double optimal_inner_radius_m;
    double total_insulation_resistance_ohm;
    double dielectric_loss_power_w;
    double breakdown_safety_factor;
    bool is_geometrically_optimal;
};

class cable_insulation_analyzer {
public:
    [[nodiscard]] static std::expected<calculation_results, calculation_error> 
    analyze(const cable_parameters& params) noexcept {
        if (params.inner_radius_m <= 0.0 || 
            params.outer_radius_m <= params.inner_radius_m || 
            params.cable_length_m <= 0.0) {
            return std::unexpected(calculation_error::invalid_geometry);
        }

        if (params.relative_permittivity < 1.0 || 
            params.breakdown_strength_v_per_m <= 0.0 || 
            params.volume_resistivity_ohm_m <= 0.0) {
            return std::unexpected(calculation_error::invalid_material_properties);
        }

        const double ratio = params.outer_radius_m / params.inner_radius_m;
        const double ln_ratio = std::log(ratio);
        const double optimal_r1 = params.outer_radius_m / std::numbers::e;

        const double e_max = params.operating_voltage_v / (params.inner_radius_m * ln_ratio);
        const double e_min = params.operating_voltage_v / (params.outer_radius_m * ln_ratio);
        const double safety_factor = params.breakdown_strength_v_per_m / e_max;

        if (safety_factor < 1.0) {
            return std::unexpected(calculation_error::dielectric_breakdown_hazard);
        }

        const double r_ins = (params.volume_resistivity_ohm_m / (2.0 * std::numbers::pi * params.cable_length_m)) * ln_ratio;
        const double capacitance = (2.0 * std::numbers::pi * epsilon_0 * params.relative_permittivity * params.cable_length_m) / ln_ratio;
        const double omega = 2.0 * std::numbers::pi * params.frequency_hz;
        const double p_loss = params.operating_voltage_v * params.operating_voltage_v * omega * capacitance * params.loss_tangent;

        const bool is_optimal = std::abs(ratio - std::numbers::e) < 0.4;

        return calculation_results{
            .max_electric_field_v_m = e_max,
            .min_electric_field_v_m = e_min,
            .radius_ratio = ratio,
            .optimal_inner_radius_m = optimal_r1,
            .total_insulation_resistance_ohm = r_ins,
            .dielectric_loss_power_w = p_loss,
            .breakdown_safety_factor = safety_factor,
            .is_geometrically_optimal = is_optimal
        };
    }
};

} // namespace insulation

int main() {
    using namespace insulation;

    constexpr cable_parameters xlpe_110kv{
        .inner_radius_m = 0.010,
        .outer_radius_m = 0.027,
        .cable_length_m = 1000.0,
        .operating_voltage_v = 110000.0,
        .frequency_hz = 50.0,
        .relative_permittivity = 2.3,
        .loss_tangent = 0.0005,
        .breakdown_strength_v_per_m = 30e6,
        .volume_resistivity_ohm_m = 1e14
    };

    const auto result = cable_insulation_analyzer::analyze(xlpe_110kv);

    if (!result) {
        switch (result.error()) {
            case calculation_error::invalid_geometry:
                std::cerr << "Помилка: некоректна геометрія провідників.\n";
                break;
            case calculation_error::invalid_material_properties:
                std::cerr << "Помилка: недопустимі параметри діелектрика.\n";
                break;
            case calculation_error::dielectric_breakdown_hazard:
                std::cerr << "УВАГА: виявлено загрозу діелектричного пробою!\n";
                break;
        }
        return 1;
    }

    const auto& res = *result;
    std::cout << std::format("=== РЕЗУЛЬТАТИ РОЗРАХУНКУ ІЗОЛЯЦІЇ КАБЕЛЮ (C++) ===\n");
    std::cout << std::format("Співвідношення r2/r1    : {:.3f} (Оптимум e ~ 2.718: {})\n", 
                             res.radius_ratio, res.is_geometrically_optimal ? "ТАК" : "НІ");
    std::cout << std::format("Оптимальний радіус r1    : {:.2f} мм\n", res.optimal_inner_radius_m * 1000.0);
    std::cout << std::format("Максимальне поле E_max   : {:.2f} кВ/мм\n", res.max_electric_field_v_m / 1e6);
    std::cout << std::format("Мінімальне поле E_min    : {:.2f} кВ/мм\n", res.min_electric_field_v_m / 1e6);
    std::cout << std::format("Запас міцності           : {:.2f}\n", res.breakdown_safety_factor);
    std::cout << std::format("Опір ізоляції (1 км)     : {:.2f} МОм\n", res.total_insulation_resistance_ohm / 1e6);
    std::cout << std::format("Потужність втрат        : {:.2f} Вт\n", res.dielectric_loss_power_w);

    return 0;
}
