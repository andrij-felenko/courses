#include <iostream>
#include <cmath>
#include <optional>
#include <string_view>
#include <iomanip>

namespace gas_dynamics {

constexpr double default_gamma = 1.4;
constexpr double default_r_gas = 287.058;

enum class flow_regime {
    subsonic_incompressible,
    subsonic_compressible,
    transonic,
    supersonic,
    hypersonic
};

[[nodiscard]] constexpr std::string_view to_string(flow_regime regime) noexcept {
    switch (regime) {
        case flow_regime::subsonic_incompressible: return "Дозвуковий (нестислий)";
        case flow_regime::subsonic_compressible:   return "Дозвуковий (стислий)";
        case flow_regime::transonic:               return "Трансзвуковий";
        case flow_regime::supersonic:              return "Надзвуковий";
        case flow_regime::hypersonic:              return "Гіперзвуковий";
    }
    return "Невідомий";
}

struct simulation_result {
    double speed_of_sound{};
    double mach_number{};
    flow_regime regime{flow_regime::subsonic_incompressible};
    double total_temperature{};
    double total_pressure{};
    double prandtl_glauert_factor{};
};

[[nodiscard]] std::optional<simulation_result> calculate(
    double velocity_m_s,
    double static_temperature_k,
    double static_pressure_pa,
    double gamma = default_gamma,
    double r_gas = default_r_gas) noexcept 
{
    if (static_temperature_k <= 0.0 || static_pressure_pa <= 0.0 || gamma <= 1.0 || r_gas <= 0.0 || velocity_m_s < 0.0) {
        return std::nullopt;
    }

    const double a = std::sqrt(gamma * r_gas * static_temperature_k);
    const double mach = velocity_m_s / a;

    flow_regime regime = flow_regime::subsonic_incompressible;
    if (mach < 0.3) {
        regime = flow_regime::subsonic_incompressible;
    } else if (mach < 0.8) {
        regime = flow_regime::subsonic_compressible;
    } else if (mach <= 1.2) {
        regime = flow_regime::transonic;
    } else if (mach <= 5.0) {
        regime = flow_regime::supersonic;
    } else {
        regime = flow_regime::hypersonic;
    }

    const double temp_ratio = 1.0 + ((gamma - 1.0) / 2.0) * mach * mach;
    const double press_ratio = std::pow(temp_ratio, gamma / (gamma - 1.0));

    const double pg_factor = (mach < 0.95) ? (1.0 / std::sqrt(1.0 - mach * mach)) : 0.0;

    return simulation_result{
        .speed_of_sound = a,
        .mach_number = mach,
        .regime = regime,
        .total_temperature = static_temperature_k * temp_ratio,
        .total_pressure = static_pressure_pa * press_ratio,
        .prandtl_glauert_factor = pg_factor
    };
}

} // namespace gas_dynamics

int main() {
    constexpr double velocity = 550.0;
    constexpr double static_temp = 216.65;
    constexpr double static_press = 22632.0;

    if (const auto res = gas_dynamics::calculate(velocity, static_temp, static_press)) {
        std::cout << std::fixed << std::setprecision(2);
        std::cout << "Швидкість потоку:    " << velocity << " м/с\n";
        std::cout << "Швидкість звуку:     " << res.speed_of_sound << " м/с\n";
        std::cout << "Число Маха:          " << std::setprecision(3) << res.mach_number << "\n";
        std::cout << "Режим течії:         " << gas_dynamics::to_string(res.regime) << "\n";
        std::cout << "Повна температура:   " << std::setprecision(2) << res.total_temperature << " K\n";
        std::cout << "Повний тиск:         " << res.total_pressure << " Па\n";
    }

    return 0;
}
