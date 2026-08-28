#include <cstdint>
#include <cmath>
#include <algorithm>
#include <expected>

namespace climate {

struct Sample {
    float temperature_c;     // °C
    float relative_humidity; // % RH
    float dew_point_c;       // °C
};

enum class ParseError {
    InvalidData
};

[[nodiscard]] inline float calculate_dew_point(float temp_c, float rh_pct) noexcept {
    constexpr float b = 17.62f;
    constexpr float c = 243.12f;
    const float safe_rh = std::clamp(rh_pct, 0.1f, 100.0f);
    
    const float gamma = std::log(safe_rh / 100.0f) + (b * temp_c) / (c + temp_c);
    return (c * gamma) / (b - gamma);
}

[[nodiscard]] inline std::expected<Sample, ParseError> parse_sht4x_raw(uint16_t raw_temp, uint16_t raw_rh) noexcept {
    const float temp = -45.0f + 175.0f * (static_cast<float>(raw_temp) / 65535.0f);
    const float raw_calc_rh = -6.0f + 125.0f * (static_cast<float>(raw_rh) / 65535.0f);
    const float rh = std::clamp(raw_calc_rh, 0.0f, 100.0f);
    
    return Sample{
        .temperature_c = temp,
        .relative_humidity = rh,
        .dew_point_c = calculate_dew_point(temp, rh)
    };
}

} // namespace climate
