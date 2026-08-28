#include <cstdint>
#include <array>
#include <expected>
#include <algorithm>
#include <span>

enum class AlsGain : std::uint8_t {
    Gain1x   = 0,
    Gain2x   = 1,
    Gain4x   = 2,
    Gain8x   = 3,
    Gain16x  = 4,
    Gain32x  = 5,
    Gain64x  = 6,
    Gain128x = 7
};

enum class AlsIntegrationTime : std::uint8_t {
    Int50ms  = 0,
    Int100ms = 1,
    Int200ms = 2,
    Int400ms = 3,
    Int800ms = 4
};

enum class AlsError {
    BusError,
    DeviceNotFound,
    DataNotReady,
    InvalidParameter
};

class AmbientLightSensor {
public:
    explicit constexpr AmbientLightSensor(float glass_attenuation = 1.0f) noexcept
        : glass_att_{std::max(1.0f, glass_attenuation)} {}

    [[nodiscard]] constexpr AlsGain gain() const noexcept { return gain_; }
    [[nodiscard]] constexpr AlsIntegrationTime integration_time() const noexcept { return int_time_; }

    [[nodiscard]] bool update_auto_range(std::uint16_t ch0_raw, bool is_overflow = false) noexcept {
        bool changed = false;

        if (is_overflow || ch0_raw > HIGH_THRESHOLD) {
            if (static_cast<std::uint8_t>(gain_) > 0) {
                gain_ = static_cast<AlsGain>(static_cast<std::uint8_t>(gain_) - 1);
                changed = true;
            } else if (static_cast<std::uint8_t>(int_time_) > 0) {
                int_time_ = static_cast<AlsIntegrationTime>(static_cast<std::uint8_t>(int_time_) - 1);
                changed = true;
            }
        } else if (ch0_raw < LOW_THRESHOLD) {
            if (static_cast<std::uint8_t>(gain_) < GAIN_MULTIPLIERS.size() - 1) {
                gain_ = static_cast<AlsGain>(static_cast<std::uint8_t>(gain_) + 1);
                changed = true;
            } else if (static_cast<std::uint8_t>(int_time_) < TIME_MULTIPLIERS.size() - 1) {
                int_time_ = static_cast<AlsIntegrationTime>(static_cast<std::uint8_t>(int_time_) + 1);
                changed = true;
            }
        }

        return changed;
    }

    [[nodiscard]] constexpr float calculate_lux(std::uint16_t ch0, std::uint16_t ch1) const noexcept {
        if (ch0 == 0) return 0.0f;

        const float ratio = static_cast<float>(ch1) / static_cast<float>(ch0);
        float a = 1.00f, b = 1.80f;

        if (ratio <= 0.15f) {
            a = 1.00f; b = 0.40f;
        } else if (ratio <= 0.45f) {
            a = 1.00f; b = 1.20f;
        } else if (ratio <= 0.75f) {
            a = 1.00f; b = 1.75f;
        } else {
            a = 0.85f; b = 1.95f;
        }

        const float net_counts = std::max(0.0f, a * static_cast<float>(ch0) - b * static_cast<float>(ch1));
        const float g_factor = GAIN_MULTIPLIERS[static_cast<std::size_t>(gain_)];
        const float t_factor = TIME_MULTIPLIERS[static_cast<std::size_t>(int_time_)];

        return (net_counts * BASE_LUX_PER_LSB / (g_factor * t_factor)) * glass_att_;
    }

private:
    static constexpr std::uint16_t LOW_THRESHOLD  = 6553;   // 10%
    static constexpr std::uint16_t HIGH_THRESHOLD = 55705;  // 85%
    static constexpr float BASE_LUX_PER_LSB       = 0.096f;

    static constexpr std::array<float, 8> GAIN_MULTIPLIERS = {
        1.0f, 2.0f, 4.0f, 8.0f, 16.0f, 32.0f, 64.0f, 128.0f
    };
    static constexpr std::array<float, 5> TIME_MULTIPLIERS = {
        0.5f, 1.0f, 2.0f, 4.0f, 8.0f
    };

    AlsGain gain_{AlsGain::Gain4x};
    AlsIntegrationTime int_time_{AlsIntegrationTime::Int100ms};
    float glass_att_{1.0f};
};
