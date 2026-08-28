#include <cstdint>
#include <array>
#include <algorithm>

class AmbientLightSensor {
public:
    explicit constexpr AmbientLightSensor(float glass_factor = 1.0f) noexcept
        : glass_factor_{std::max(1.0f, glass_factor)} {}

    [[nodiscard]] bool update_range(std::uint16_t ch0_raw, bool overflow) noexcept {
        bool reconfigure = false;
        if (overflow || ch0_raw > HIGH_THRESHOLD) {
            if (gain_idx_ > 0) {
                --gain_idx_;
                reconfigure = true;
            } else if (tint_idx_ > 0) {
                --tint_idx_;
                reconfigure = true;
            }
        } else if (ch0_raw < LOW_THRESHOLD) {
            if (gain_idx_ < GAINS.size() - 1) {
                ++gain_idx_;
                reconfigure = true;
            } else if (tint_idx_ < TINTS.size() - 1) {
                ++tint_idx_;
                reconfigure = true;
            }
        }
        return reconfigure;
    }

    [[nodiscard]] constexpr float calculate_lux(std::uint16_t ch0, std::uint16_t ch1) const noexcept {
        if (ch0 == 0) return 0.0f;
        const float ratio = static_cast<float>(ch1) / static_cast<float>(ch0);
        float a = 1.0f, b = 1.8f;
        if (ratio <= 0.20f) { a = 1.0f; b = 0.5f; }
        else if (ratio <= 0.60f) { a = 1.0f; b = 1.3f; }

        const float net = std::max(0.0f, a * static_cast<float>(ch0) - b * static_cast<float>(ch1));
        const float lsb = (BASE_LSB / (GAINS[gain_idx_] * TINTS[tint_idx_])) * glass_factor_;
        return net * lsb;
    }

private:
    static constexpr std::uint16_t LOW_THRESHOLD  = 6553;
    static constexpr std::uint16_t HIGH_THRESHOLD = 55705;
    static constexpr float BASE_LSB               = 0.096f;

    static constexpr std::array<float, 4> GAINS = {1.0f, 4.0f, 16.0f, 128.0f};
    static constexpr std::array<float, 3> TINTS = {0.5f, 1.0f, 4.0f};

    std::size_t gain_idx_{1};
    std::size_t tint_idx_{1};
    float glass_factor_{1.0f};
};
