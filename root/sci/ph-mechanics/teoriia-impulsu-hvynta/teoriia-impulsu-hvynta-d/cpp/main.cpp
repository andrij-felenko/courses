#include <iostream>
#include <iomanip>
#include <numbers>
#include <cmath>
#include <string_view>
#include <span>
#include <expected>

struct HoverSpec {
    std::string_view label;
    float thrust_newtons;    // необхідна тяга T, Н
    float radius_meters;     // радіус диска R, м
    float air_density;       // густина середовища rho, кг/м³
    float figure_of_merit;   // коефіцієнт досконалості FM (0 < FM <= 1)
};

struct HoverMetrics {
    float disk_area_m2;
    float disk_loading_pa;
    float induced_velocity_m_s;
    float wake_velocity_m_s;
    float ideal_power_watts;
    float actual_shaft_watts;
    float power_loading_n_per_kw;
    float power_loading_grams_per_watt;
};

enum class ComputeError {
    InvalidThrust,
    InvalidGeometry,
    InvalidDensity,
    InvalidFigureOfMerit
};

[[nodiscard]] constexpr std::expected<HoverMetrics, ComputeError>
evaluate_hover(const HoverSpec& spec) noexcept {
    if (spec.thrust_newtons <= 0.0f) return std::unexpected(ComputeError::InvalidThrust);
    if (spec.radius_meters <= 0.0f) return std::unexpected(ComputeError::InvalidGeometry);
    if (spec.air_density <= 0.0f) return std::unexpected(ComputeError::InvalidDensity);
    if (spec.figure_of_merit <= 0.0f || spec.figure_of_merit > 1.0f) {
        return std::unexpected(ComputeError::InvalidFigureOfMerit);
    }

    constexpr float pi = std::numbers::pi_v<float>;
    constexpr float g_accel = 9.80665f;

    const float area = pi * spec.radius_meters * spec.radius_meters;
    const float disk_loading = spec.thrust_newtons / area;
    
    // v_i = sqrt( T / (2 * rho * A) )
    const float v_induced = std::sqrt(spec.thrust_newtons / (2.0f * spec.air_density * area));
    const float v_wake = 2.0f * v_induced;

    // P_i = T * v_i
    const float p_ideal = spec.thrust_newtons * v_induced;
    const float p_actual = p_ideal / spec.figure_of_merit;

    const float pl_n_kw = (spec.thrust_newtons / p_actual) * 1000.0f;
    const float pl_g_w = (spec.thrust_newtons / (p_actual * g_accel)) * 1000.0f;

    return HoverMetrics{
        .disk_area_m2 = area,
        .disk_loading_pa = disk_loading,
        .induced_velocity_m_s = v_induced,
        .wake_velocity_m_s = v_wake,
        .ideal_power_watts = p_ideal,
        .actual_shaft_watts = p_actual,
        .power_loading_n_per_kw = pl_n_kw,
        .power_loading_grams_per_watt = pl_g_w
    };
}

void print_comparison_table(std::span<const HoverSpec> specs) {
    std::cout << std::fixed << std::setprecision(2);
    std::cout << "========================================================================================\n";
    std::cout << std::left << std::setw(32) << "Конфігурація ротора"
              << std::right << std::setw(10) << "D (дюйм)"
              << std::setw(12) << "DL (Па)"
              << std::setw(12) << "v_i (м/с)"
              << std::setw(12) << "P_sha (Вт)"
              << std::setw(14) << "PL (г/Вт)\n";
    std::cout << "========================================================================================\n";

    for (const auto& spec : specs) {
        auto result = evaluate_hover(spec);
        if (!result) {
            std::cerr << "Помилка розрахунку для " << spec.label << "\n";
            continue;
        }

        const auto& m = *result;
        const float diam_inches = (spec.radius_meters * 2.0f) / 0.0254f;

        std::cout << std::left << std::setw(32) << spec.label
                  << std::right << std::setw(10) << diam_inches
                  << std::setw(12) << m.disk_loading_pa
                  << std::setw(12) << m.induced_velocity_m_s
                  << std::setw(12) << m.actual_shaft_watts
                  << std::setw(14) << m.power_loading_grams_per_watt
                  << "\n";
    }
    std::cout << "========================================================================================\n";
}

int main() {
    constexpr float rho_std = 1.225f;
    constexpr float target_thrust = 10.0f; // 10 Н на ротор (~1.02 кг тяги)

    const HoverSpec fleet[] = {
        { "FPV Racing (5\")",          target_thrust, 0.0635f, rho_std, 0.55f },
        { "Cinelifter (8\")",          target_thrust, 0.1016f, rho_std, 0.60f },
        { "DJI Commercial (15\")",     target_thrust, 0.1905f, rho_std, 0.68f },
        { "Heavy-Lift Agras (30\")",   target_thrust, 0.3810f, rho_std, 0.75f },
        { "UAV Helicopter (60\")",     target_thrust, 0.7620f, rho_std, 0.80f }
    };

    print_comparison_table(fleet);
    return 0;
}
