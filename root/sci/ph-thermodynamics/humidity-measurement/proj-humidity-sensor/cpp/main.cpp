#include <iostream>
#include <cmath>
#include <optional>
#include <expected>
#include <string_view>
#include <algorithm>

namespace physics {

struct SensorCalibration {
    float temp_coefficient{0.15f}; // % RH / °C
    float ref_temperature_c{25.0f};
};

struct PsychrometricState {
    float temperature_c;       // °C
    float relative_humidity;   // %
    float sat_vapor_pressure;  // Pa
    float vapor_pressure;      // Pa
    float dew_point_c;         // °C
    float absolute_humidity;   // g/m³
    float enthalpy_kj_kg;      // kJ/kg
};

enum class HumidityError {
    TemperatureOutOfRange,
    HumidityOutOfRange,
    InvalidPressure
};

class HumidityCalculator {
public:
    explicit constexpr HumidityCalculator(SensorCalibration cal = {}) noexcept
        : cal_(cal) {}

    [[nodiscard]] std::expected<PsychrometricState, HumidityError> calculate(
        float temp_c, float rh_raw, float atm_pressure_pa = 101325.0f
    ) const noexcept {
        if (temp_c < -50.0f || temp_c > 100.0f) {
            return std::unexpected(HumidityError::TemperatureOutOfRange);
        }
        if (rh_raw < -10.0f || rh_raw > 110.0f) {
            return std::unexpected(HumidityError::HumidityOutOfRange);
        }
        if (atm_pressure_pa < 30000.0f || atm_pressure_pa > 150000.0f) {
            return std::unexpected(HumidityError::InvalidPressure);
        }

        // 1. Термокомпенсація вологості
        float rh_comp = rh_raw - (temp_c - cal_.ref_temperature_c) * cal_.temp_coefficient;
        rh_comp = std::clamp(rh_comp, 0.0f, 100.0f);

        // 2. Розрахунок тиску насичення
        float p_sat = calc_saturation_pressure(temp_c);
        float p_v = (rh_comp / 100.0f) * p_sat;

        // 3. Розрахунок точки роси
        float dew_point = calc_dew_point(temp_c, rh_comp);

        // 4. Абсолютна вологість та ентальпія
        float abs_hum = 2.1667f * (p_v / (temp_c + 273.15f));
        float w_kg_kg = 0.62198f * (p_v / (atm_pressure_pa - p_v));
        float enthalpy = 1.006f * temp_c + w_kg_kg * (2501.0f + 1.86f * temp_c);

        return PsychrometricState{
            .temperature_c = temp_c,
            .relative_humidity = rh_comp,
            .sat_vapor_pressure = p_sat,
            .vapor_pressure = p_v,
            .dew_point_c = dew_point,
            .absolute_humidity = abs_hum,
            .enthalpy_kj_kg = enthalpy
        };
    }

private:
    SensorCalibration cal_;

    [[nodiscard]] static constexpr float calc_saturation_pressure(float temp_c) noexcept {
        float a = (temp_c >= 0.0f) ? 611.21f : 611.15f;
        float b = (temp_c >= 0.0f) ? 17.502f : 22.452f;
        float c = (temp_c >= 0.0f) ? 240.97f : 272.55f;
        return a * std::exp((b * temp_c) / (c + temp_c));
    }

    [[nodiscard]] static float calc_dew_point(float temp_c, float rh_percent) noexcept {
        float safe_rh = std::clamp(rh_percent, 0.01f, 100.0f);
        float b = (temp_c >= 0.0f) ? 17.502f : 22.452f;
        float c = (temp_c >= 0.0f) ? 240.97f : 272.55f;

        float gamma = (b * temp_c) / (c + temp_c) + std::log(safe_rh / 100.0f);
        return (c * gamma) / (b - gamma);
    }
};

} // namespace physics

int main() {
    using namespace physics;
    
    HumidityCalculator calc{SensorCalibration{.temp_coefficient = 0.15f, .ref_temperature_c = 25.0f}};
    
    auto result = calc.calculate(30.0f, 50.0f);
    if (result) {
        const auto& state = *result;
        std::cout << "--- Термодинамічний стан (C++17/23) ---\n";
        std::cout << "Температура:          " << state.temperature_c << " °C\n";
        std::cout << "Відносна вологість:   " << state.relative_humidity << " %\n";
        std::cout << "Тиск насичення:       " << state.sat_vapor_pressure << " Па\n";
        std::cout << "Парціальний тиск:     " << state.vapor_pressure << " Па\n";
        std::cout << "Точка роси:           " << state.dew_point_c << " °C\n";
        std::cout << "Абсолютна вологість:  " << state.absolute_humidity << " г/м³\n";
        std::cout << "Ентальпія повітря:    " << state.enthalpy_kj_kg << " кДж/кг\n";
    }
    return 0;
}
