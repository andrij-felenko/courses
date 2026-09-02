#include "power.hpp"

#include <algorithm>
#include <cmath>
#include <numbers>
#include <type_traits>

namespace mission {

float air_density(float alt_msl_m) noexcept
{
    // Стандартна атмосфера ISA до тропопаузи.
    const float ratio = 1.0f - 2.25577e-5f * alt_msl_m;
    return ratio <= 0.0f ? 0.0f : 1.225f * std::pow(ratio, 4.2559f);
}

std::pair<float, float> Aircraft::polar_coefficients(const FixedWing& wing, float rho) const noexcept
{
    const float weight_n = spec_.mass_kg * kGravity;
    const float a = 0.5f * rho * wing.wing_area_m2 * wing.cd0;                 // паразитарний
    const float b = 2.0f * weight_n * weight_n /
                    (rho * std::numbers::pi_v<float> * wing.span_m * wing.span_m * wing.oswald_e);
    return {a, b};                                                            // індуктивний
}

float Aircraft::level_power_w(float airspeed_mps, float rho) const noexcept
{
    if (airspeed_mps < 0.1f || rho <= 0.0f) {
        return loiter_power_w(rho);
    }

    const float shaft_w = std::visit(
        [&](const auto& aero) -> float {
            using T = std::decay_t<decltype(aero)>;
            if constexpr (std::is_same_v<T, FixedWing>) {
                const auto [a, b] = polar_coefficients(aero, rho);
                return a * airspeed_mps * airspeed_mps * airspeed_mps + b / airspeed_mps;
            } else {
                const float weight_n = spec_.mass_kg * kGravity;
                const float hover_w =
                    std::pow(weight_n, 1.5f) / std::sqrt(2.0f * rho * aero.disk_area_m2);
                // Нахилений корпус коптера підставляє потоку більшу площу.
                return hover_w + aero.body_drag_k * airspeed_mps * airspeed_mps * airspeed_mps;
            }
        },
        spec_.aerodynamics);

    return shaft_w / spec_.eta_prop;
}

float Aircraft::climb_power_w(float climb_rate_mps) const noexcept
{
    // Зниження енергії не повертає: рекуперації на гвинті немає.
    if (climb_rate_mps <= 0.0f) {
        return 0.0f;
    }
    return spec_.mass_kg * kGravity * climb_rate_mps / spec_.eta_prop;
}

float Aircraft::loiter_power_w(float rho) const noexcept
{
    if (rho <= 0.0f) {
        rho = 1.225f;
    }

    if (const auto* copter = std::get_if<Multirotor>(&spec_.aerodynamics)) {
        const float weight_n = spec_.mass_kg * kGravity;
        return std::pow(weight_n, 1.5f) /
               std::sqrt(2.0f * rho * copter->disk_area_m2) / spec_.eta_prop;
    }

    // Літак «стоїть» на точці віражем на швидкості мінімальної потужності.
    const float v_mp = std::clamp(best_endurance_speed(rho).value_or(spec_.airspeed_min_mps),
                                  spec_.airspeed_min_mps, spec_.airspeed_max_mps);
    return level_power_w(v_mp, rho);
}

std::optional<float> Aircraft::best_endurance_speed(float rho) const noexcept
{
    const auto* wing = std::get_if<FixedWing>(&spec_.aerodynamics);
    if (wing == nullptr || rho <= 0.0f) {
        return std::nullopt;
    }
    const auto [a, b] = polar_coefficients(*wing, rho);
    return std::pow(b / (3.0f * a), 0.25f);
}

std::optional<float> Aircraft::best_range_speed(float rho) const noexcept
{
    const auto* wing = std::get_if<FixedWing>(&spec_.aerodynamics);
    if (wing == nullptr || rho <= 0.0f) {
        return std::nullopt;
    }
    const auto [a, b] = polar_coefficients(*wing, rho);
    return std::pow(b / a, 0.25f);
}

float Battery::temperature_factor() const noexcept
{
    // Нижче +10 °C зростає внутрішній опір і падає віддача ємності.
    if (spec_.pack_temp_c >= 10.0f) {
        return 1.0f;
    }
    if (spec_.pack_temp_c <= -10.0f) {
        return 0.70f;
    }
    return 1.0f - (10.0f - spec_.pack_temp_c) * 0.015f;
}

std::expected<float, Failure> Battery::current_a(float load_w) const noexcept
{
    if (load_w <= 0.0f) {
        return 0.0f;
    }
    if (spec_.internal_r_ohm <= 1.0e-4f) {
        return load_w / spec_.nominal_v;
    }

    // V*I - I^2*R = P; беремо менший корінь — робочу гілку.
    const float disc = spec_.nominal_v * spec_.nominal_v - 4.0f * spec_.internal_r_ohm * load_w;
    if (disc <= 0.0f) {
        return std::unexpected(Failure::PowerUnreachable);
    }
    return (spec_.nominal_v - std::sqrt(disc)) / (2.0f * spec_.internal_r_ohm);
}

float Battery::delivered_wh(float avg_current_a) const noexcept
{
    float capacity_ah = spec_.capacity_ah;

    // Закон Пейкерта: під більшим струмом пакет віддає менше ампер-годин.
    // Втрати на R_int уже сидять усередині цього коефіцієнта.
    if (avg_current_a > spec_.ref_current_a && spec_.peukert_k > 1.0f && spec_.ref_current_a > 0.0f) {
        capacity_ah *= std::pow(spec_.ref_current_a / avg_current_a, spec_.peukert_k - 1.0f);
    }

    return capacity_ah * spec_.nominal_v * temperature_factor() * spec_.health;
}

float Battery::usable_wh(float avg_current_a) const noexcept
{
    return delivered_wh(avg_current_a) * (1.0f - spec_.reserve_margin);
}

}  // namespace mission
