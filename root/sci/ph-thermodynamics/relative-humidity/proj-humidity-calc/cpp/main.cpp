#include <cmath>
#include <expected>
#include <iostream>
#include <format>
#include <algorithm>

namespace humidity {

// Константи алгоритму Магнуса та психрометрії
constexpr double MAGNUS_A = 6.112;    // гПа
constexpr double MAGNUS_B = 17.67;
constexpr double MAGNUS_C = 243.5;    // °C
constexpr double PSYCHRO_A = 0.000662; // К⁻¹

enum class CalculationError {
    InvalidTemperature,
    InvalidHumidity,
    InvalidPressure
};

// Обчислення тиску насиченої пари (гПа)
[[nodiscard]] constexpr double saturation_vapor_pressure(double temp_celsius) noexcept {
    return MAGNUS_A * std::exp((MAGNUS_B * temp_celsius) / (MAGNUS_C + temp_celsius));
}

// Розрахунок точки роси (°C) із перевіркою діапазонів входів
[[nodiscard]] std::expected<double, CalculationError> dew_point(double temp_celsius, double relative_humidity_pct) noexcept {
    if (relative_humidity_pct <= 0.0 || relative_humidity_pct > 100.0) {
        return std::unexpected(CalculationError::InvalidHumidity);
    }
    if (temp_celsius < -80.0 || temp_celsius > 85.0) {
        return std::unexpected(CalculationError::InvalidTemperature);
    }

    const double gamma = std::log(relative_humidity_pct / 100.0) + 
                         (MAGNUS_B * temp_celsius) / (MAGNUS_C + temp_celsius);
    
    return (MAGNUS_C * gamma) / (MAGNUS_B - gamma);
}

// Розрахунок відносної вологості за показами психрометра
[[nodiscard]] std::expected<double, CalculationError> relative_humidity_psychrometric(
    double t_dry, double t_wet, double pressure_hpa = 1013.25) noexcept {
    
    if (t_wet > t_dry) {
        return std::unexpected(CalculationError::InvalidTemperature);
    }
    if (pressure_hpa < 300.0 || pressure_hpa > 1200.0) {
        return std::unexpected(CalculationError::InvalidPressure);
    }

    const double e_s_wet = saturation_vapor_pressure(t_wet);
    const double e_s_dry = saturation_vapor_pressure(t_dry);
    const double actual_e = e_s_wet - PSYCHRO_A * pressure_hpa * (t_dry - t_wet);

    const double rh = (actual_e / e_s_dry) * 100.0;
    return std::clamp(rh, 0.0, 100.0);
}

} // namespace humidity

int main() {
    constexpr double t_dry = 25.0;
    constexpr double t_wet = 18.5;
    constexpr double pressure = 1013.25;

    const auto rh_res = humidity::relative_humidity_psychrometric(t_dry, t_wet, pressure);
    if (rh_res) {
        std::cout << std::format("Сухий: {:.1f}°C, Вологий: {:.1f}°C -> RH = {:.2f}%\n", 
                                 t_dry, t_wet, *rh_res);
        
        const auto td_res = humidity::dew_point(t_dry, *rh_res);
        if (td_res) {
            std::cout << std::format("Точка роси T_d = {:.2f}°C\n", *td_res);
        }
    }
    return 0;
}
