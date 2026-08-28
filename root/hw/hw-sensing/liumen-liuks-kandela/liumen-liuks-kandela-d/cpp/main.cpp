#include <cstdint>
#include <optional>
#include <cmath>
#include <algorithm>

namespace sensing {

enum class LightSourceType {
    Sunlight,
    Incandescent,
    Fluorescent,
    WhiteLed
};

struct AlsRawReading {
    std::uint32_t raw_visible_plus_ir{0}; // Канал CH0
    std::uint32_t raw_ir_only{0};         // Канал CH1
    double integration_time_ms{100.0};
    double sensor_gain{1.0};
};

class PhotometricCalculator {
public:
    [[nodiscard]] static std::optional<double> calculateLux(
        const AlsRawReading& reading,
        LightSourceType src = LightSourceType::WhiteLed) noexcept
    {
        if (reading.integration_time_ms <= 0.0 || reading.sensor_gain <= 0.0) {
            return std::nullopt;
        }

        const double norm_factor = (100.0 / reading.integration_time_ms) * (1.0 / reading.sensor_gain);
        const double ch0 = static_cast<double>(reading.raw_visible_plus_ir) * norm_factor;
        const double ch1 = static_cast<double>(reading.raw_ir_only) * norm_factor;

        if (ch0 < 1e-6) {
            return 0.0;
        }

        const double ir_ratio = ch1 / ch0;
        double lux = 0.0;

        if (ir_ratio < 0.50) {
            lux = 0.0304 * ch0 - 0.0620 * ch0 * std::pow(ir_ratio, 1.4);
        } else if (ir_ratio < 0.80) {
            lux = 0.0224 * ch0 - 0.0310 * ch1;
        } else if (ir_ratio < 1.30) {
            lux = 0.0128 * ch0 - 0.0153 * ch1;
        } else {
            lux = 0.0;
        }

        return std::max(0.0, lux);
    }
};

} // namespace sensing
