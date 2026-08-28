#include <cmath>
#include <expected>
#include <iomanip>
#include <iostream>
#include <numbers>
#include <string_view>

namespace aero {

// Геометрична специфікація пропелера (SI)
struct PropellerSpec {
    double diameter_m;     // Зовнішній діаметр D, м
    double pitch_m;        // Геометричний крок P, м
    double ct0;            // Статичний коефіцієнт тяги (J = 0)
    double cp0;            // Базовий коефіцієнт профільної потужності

    [[nodiscard]] constexpr double pitch_to_diameter_ratio() const noexcept {
        return (diameter_m > 0.0) ? (pitch_m / diameter_m) : 0.0;
    }
};

// Розрахований робочий стан гвинта в польоті
struct PropellerState {
    double advance_ratio;  // Коефіцієнт поступу J
    double thrust_n;       // Тяга T, Н
    double power_w;        // Механічна потужність на валу P, Вт
    double efficiency;     // Пропульсивний ККД eta
    bool is_windmilling;   // Ознака режиму вітряка / гальмування (T < 0)
};

enum class CalculationError {
    InvalidGeometry,
    InvalidRpm,
    InvalidAirDensity
};

// Обчислення аеродинамічних сил пропелера
[[nodiscard]] constexpr std::expected<PropellerState, CalculationError> calculate_propeller_state(
    const PropellerSpec& spec,
    double forward_speed_mps,
    double rpm,
    double air_density = 1.225
) noexcept {
    if (spec.diameter_m <= 0.0 || spec.pitch_m <= 0.0) {
        return std::unexpected(CalculationError::InvalidGeometry);
    }
    if (rpm <= 0.0) {
        return std::unexpected(CalculationError::InvalidRpm);
    }
    if (air_density <= 0.0) {
        return std::unexpected(CalculationError::InvalidAirDensity);
    }

    const double n = rpm / 60.0; // Частота обертання, об/с
    const double d = spec.diameter_m;
    const double p = spec.pitch_m;
    const double v0 = (forward_speed_mps < 0.0) ? 0.0 : forward_speed_mps;

    // Безрозмірний коефіцієнт поступу J = V0 / (n * D)
    const double j = v0 / (n * d);

    // Точка нульової тяги J_zero ≈ P / D
    const double j_zero = p / d;

    // Розрахунок коефіцієнта тяги C_T(J)
    const double ct = spec.ct0 * (1.0 - (j / j_zero));

    // Розрахунок коефіцієнта потужності C_P(J)
    double cp = spec.cp0;
    if (ct > 0.0) {
        cp += 0.95 * j * ct;
    }

    // Масштабування в абсолютні величини за законами аеродинамічної подібності
    const double d4 = std::pow(d, 4);
    const double d5 = d4 * d;
    const double n2 = n * n;
    const double n3 = n2 * n;

    const double thrust = ct * air_density * n2 * d4;
    const double power = cp * air_density * n3 * d5;

    // Пропульсивний ККД: eta = (T * V0) / P
    double efficiency = 0.0;
    if (power > 1e-3 && thrust > 0.0 && v0 > 0.0) {
        efficiency = (thrust * v0) / power;
        if (efficiency > 0.90) {
            efficiency = 0.90; // Фізична межа максимального ККД лопатей
        }
    }

    return PropellerState{
        .advance_ratio = j,
        .thrust_n = thrust,
        .power_w = power,
        .efficiency = efficiency,
        .is_windmilling = (thrust < 0.0)
    };
}

} // namespace aero

int main() {
    // Карбоновий швидкісний FPV-пропелер 7x7 дюймів (D=0.1778м, P=0.1778м)
    constexpr aero::PropellerSpec speed_prop{
        .diameter_m = 0.1778,
        .pitch_m = 0.1778,
        .ct0 = 0.115,
        .cp0 = 0.045
    };

    constexpr double rpm = 18000.0;
    constexpr double rho = 1.225;

    std::cout << std::fixed << std::setprecision(2);
    std::cout << "=== Продування швидкісного гвинта 7x7 (P/D = "
              << speed_prop.pitch_to_diameter_ratio() << ") при "
              << static_cast<int>(rpm) << " RPM ===\n";
    std::cout << " V0 (м/с) | V0 (км/год) |   J   | Тяга (Н) | Потужність (Вт) |  ККД (%)\n";
    std::cout << "----------+-------------+-------+----------+-----------------+----------\n";

    for (double v = 0.0; v <= 60.0; v += 10.0) {
        auto result = aero::calculate_propeller_state(speed_prop, v, rpm, rho);
        if (result.has_value()) {
            const auto& state = result.value();
            std::cout << "  " << std::setw(5) << v << "   |   "
                      << std::setw(6) << (v * 3.6) << "    |  "
                      << std::setw(4) << state.advance_ratio << " |  "
                      << std::setw(6) << state.thrust_n << "  |     "
                      << std::setw(6) << state.power_w << "      |  "
                      << std::setw(5) << (state.efficiency * 100.0) << "%\n";
        }
    }

    return 0;
}
