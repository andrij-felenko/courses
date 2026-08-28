#include <iostream>
#include <cmath>
#include <numbers>
#include <expected>
#include <string_view>
#include <format>

namespace electrodynamics {

constexpr double mu_0 = 4.0 * std::numbers::pi * 1e-7;
constexpr double sqrt3_half = 0.8660254037844386;

enum class CalculationError {
    InvalidDimensions,
    InvalidCurrent,
    StressExceeded,
    InsulatorOverload
};

struct BusbarGeometry {
    double distance_m;    // Відстань між осями фаз a, м
    double span_length_m; // Довжина прольоту між ізоляторами L, м
    double width_m;       // Товщина шини b, м
    double height_m;      // Висота шини h, м

    [[nodiscard]] constexpr double section_modulus() const noexcept {
        return (width_m * height_m * height_m) / 6.0; // W_z, м^3
    }
};

struct MaterialLimits {
    double yield_stress_mpa;       // Межа плинності sigma_0.2, МПа
    double max_insulator_force_kn; // Допустиме зусилля ізолятора, кН
    std::string_view material_name;
};

struct ShortCircuitParams {
    double initial_ik_ka; // Початковий діючий струм КЗ I''k, кА
    double shock_factor;  // Ударний коефіцієнт k_th
};

struct CalculationResult {
    double peak_current_ka;
    double force_per_meter_kn;
    double total_span_force_kn;
    double bending_stress_mpa;
    double insulator_load_kn;
    double safety_factor;
    bool is_safe;
};

class BusbarCalculator {
public:
    [[nodiscard]] static std::expected<CalculationResult, CalculationError>
    calculate(const BusbarGeometry& geo, 
              const MaterialLimits& mat, 
              const ShortCircuitParams& sc) noexcept 
    {
        if (geo.distance_m <= 0.0 || geo.span_length_m <= 0.0 || 
            geo.width_m <= 0.0 || geo.height_m <= 0.0) {
            return std::unexpected(CalculationError::InvalidDimensions);
        }
        if (sc.initial_ik_ka <= 0.0 || sc.shock_factor < 1.0) {
            return std::unexpected(CalculationError::InvalidCurrent);
        }

        // 1. Ударний струм i_th у амперах
        const double i_peak_amp = sc.initial_ik_ka * 1000.0 * 
                                  std::numbers::sqrt2 * sc.shock_factor;

        // 2. Сила на метр F_din у Н/м
        const double f_din_n_m = (mu_0 / (2.0 * std::numbers::pi)) * 
                                 sqrt3_half * 
                                 (i_peak_amp * i_peak_amp / geo.distance_m);

        // 3. Згинний момент M_max у Н*м
        const double m_max = (f_din_n_m * geo.span_length_m * geo.span_length_m) / 10.0;

        // 4. Механічне напруження у МПа
        const double stress_mpa = (m_max / geo.section_modulus()) / 1e6;

        // 5. Навантаження на ізолятор у кН
        const double insulator_kn = 1.1 * (f_din_n_m / 1000.0) * geo.span_length_m;

        const double safety_factor = mat.yield_stress_mpa / stress_mpa;
        const bool is_safe = (stress_mpa <= 0.8 * mat.yield_stress_mpa) && 
                             (insulator_kn <= mat.max_insulator_force_kn);

        CalculationResult res{
            .peak_current_ka = i_peak_amp / 1000.0,
            .force_per_meter_kn = f_din_n_m / 1000.0,
            .total_span_force_kn = (f_din_n_m / 1000.0) * geo.span_length_m,
            .bending_stress_mpa = stress_mpa,
            .insulator_load_kn = insulator_kn,
            .safety_factor = safety_factor,
            .is_safe = is_safe
        };

        if (stress_mpa > mat.yield_stress_mpa) {
            return std::unexpected(CalculationError::StressExceeded);
        }
        if (insulator_kn > mat.max_insulator_force_kn) {
            return std::unexpected(CalculationError::InsulatorOverload);
        }

        return res;
    }
};

} // namespace electrodynamics

int main() {
    using namespace electrodynamics;

    constexpr BusbarGeometry geo{
        .distance_m = 0.25,
        .span_length_m = 1.2,
        .width_m = 0.010,
        .height_m = 0.080
    };

    constexpr MaterialLimits mat{
        .yield_stress_mpa = 200.0,
        .max_insulator_force_kn = 12.5,
        .material_name = "Мідь M1t"
    };

    constexpr ShortCircuitParams sc{
        .initial_ik_ka = 40.0,
        .shock_factor = 1.8
    };

    const auto result = BusbarCalculator::calculate(geo, mat, sc);

    if (result) {
        std::cout << std::format("--- РЕЗУЛЬТАТ РОЗРАХУНКУ ШИНОПРОВОДУ (C++20) ---\n"
                                 "Матеріал шин:                 {}\n"
                                 "Ударний струм КЗ i_th:        {:.2f} кА\n"
                                 "Сила на метр F_din:            {:.2f} кН/м\n"
                                 "Напруження вигину sigma:       {:.2f} МПа\n"
                                 "Навантаження на ізолятор:     {:.2f} кН\n"
                                 "Коефіцієнт запасу:             {:.2f}\n"
                                 "Стан конструкції:              {}\n",
                                 mat.material_name,
                                 result->peak_current_ka,
                                 result->force_per_meter_kn,
                                 result->bending_stress_mpa,
                                 result->insulator_load_kn,
                                 result->safety_factor,
                                 result->is_safe ? " БЕЗПЕЧНО" : " РИЗИК РУЙНУВАННЯ");
    } else {
        std::cerr << "Помилка розрахунку шинопроводу! Код помилки: " 
                  << static_cast<int>(result.error()) << '\n';
        return 1;
    }

    return 0;
}
