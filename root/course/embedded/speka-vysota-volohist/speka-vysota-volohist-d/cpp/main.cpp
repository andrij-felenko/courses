#include <iostream>
#include <cmath>
#include <numbers>
#include <expected>
#include <string_view>
#include <format>

namespace aero {

// Фізичні константи Міжнародної стандартної атмосфери ISA
inline constexpr float isa_p0_pa        = 101325.0f;
inline constexpr float isa_t0_k         = 288.15f;
inline constexpr float isa_rho0         = 1.2250f;
inline constexpr float gas_const_dry    = 287.058f;
inline constexpr float density_exp      = 0.23497f;
inline constexpr float pressure_exp     = 0.190263f;
inline constexpr float scale_height_m   = 44330.8f;

struct FlightEnv {
    float pressure_hpa;     // Барометричний тиск, гПа
    float temp_celsius;     // Температура повітря, °C
    float rel_humidity_pct; // Відносна вологість, % (0..100)
    float nominal_twr;      // Номінальний TWR на рівні моря ISA
    float nominal_time_min; // Номінальний час польоту ISA, хв
};

struct FlightReport {
    float air_density_kg_m3;
    float density_ratio;
    float pressure_alt_m;
    float density_alt_m;
    float actual_twr;
    float hover_rpm_multiplier;
    float hover_current_multiplier;
    float copper_heat_multiplier;
    float estimated_time_min;
    bool  is_safe_to_fly;
};

enum class InputError {
    InvalidPressure,
    InvalidTemperature,
    InvalidHumidity,
    InvalidTwr
};

[[nodiscard]] constexpr std::expected<FlightReport, InputError>
evaluate_flight_conditions(const FlightEnv& env) noexcept {
    if (env.pressure_hpa < 300.0f || env.pressure_hpa > 1100.0f) {
        return std::unexpected(InputError::InvalidPressure);
    }
    if (env.temp_celsius < -50.0f || env.temp_celsius > 65.0f) {
        return std::unexpected(InputError::InvalidTemperature);
    }
    if (env.rel_humidity_pct < 0.0f || env.rel_humidity_pct > 100.0f) {
        return std::unexpected(InputError::InvalidHumidity);
    }
    if (env.nominal_twr <= 0.5f) {
        return std::unexpected(InputError::InvalidTwr);
    }

    const float p_pa = env.pressure_hpa * 100.0f;
    const float t_k  = env.temp_celsius + 273.15f;

    // Тиск насиченої пари (Магнус-Тетенс)
    const float p_sat_pa = 610.78f * std::exp((17.27f * env.temp_celsius) / (237.3f + env.temp_celsius));
    const float p_v_pa   = (env.rel_humidity_pct / 100.0f) * p_sat_pa;

    // Густина вологого повітря за законом Дальтона
    const float rho = (p_pa / (gas_const_dry * t_k)) * (1.0f - 0.37803f * (p_v_pa / p_pa));
    const float rho_rel = rho / isa_rho0;

    const float p_alt_m = scale_height_m * (1.0f - std::pow(p_pa / isa_p0_pa, pressure_exp));
    const float d_alt_m = scale_height_m * (1.0f - std::pow(rho_rel, density_exp));

    const float actual_twr = env.nominal_twr * rho_rel;
    const float hover_scale = 1.0f / std::sqrt(rho_rel);

    return FlightReport{
        .air_density_kg_m3       = rho,
        .density_ratio           = rho_rel,
        .pressure_alt_m          = p_alt_m,
        .density_alt_m           = d_alt_m,
        .actual_twr              = actual_twr,
        .hover_rpm_multiplier    = hover_scale,
        .hover_current_multiplier= hover_scale,
        .copper_heat_multiplier  = 1.0f / rho_rel,
        .estimated_time_min      = env.nominal_time_min * std::pow(rho_rel, 0.75f),
        .is_safe_to_fly          = (actual_twr >= 1.40f)
    };
}

} // namespace aero
