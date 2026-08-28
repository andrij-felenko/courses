// info_thermo_api.hpp - Заголовочний інтерфейс термодинаміки інформації C++20
#pragma once

#include <numbers>
#include <expected>
#include <string_view>
#include <cstdint>

namespace thermo::api {

constexpr double kBoltzmann = 1.380649e-23;       // Дж/К
constexpr double kElemCharge = 1.602176634e-19;   // Кл
constexpr double kLn2 = std::numbers::ln2;

enum class ApiError : int8_t {
    InvalidTemperature = -1,
    NegativeInformation = -2,
    NullPointer = -3
};

struct EngineParams {
    double temperature_K{300.0};
    double mutual_info_bits{1.0};
    double free_energy_diff_J{0.0};
    double efficiency_factor{1.0};
};

struct EngineResult {
    double max_work_theoretical_J;
    double actual_work_extracted_J;
    double min_erasure_heat_J;
    double min_erasure_heat_meV;
    double net_entropy_universe_JK;
};

// Ідіоматична обгортка C++20 з використанням std::expected
[[nodiscard]] std::expected<EngineResult, ApiError> calculate(const EngineParams& params) noexcept;

[[nodiscard]] constexpr double landauer_limit_meV(double temp_K) noexcept {
    if (temp_K <= 0.0) return -1.0;
    return (kBoltzmann * temp_K * kLn2 / kElemCharge) * 1000.0;
}

} // namespace thermo::api
:::

#### Приклад виконання обчислень

Нижче наведено приклади використання API мовами C та C++20:

:::tabs
