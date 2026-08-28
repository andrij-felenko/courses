#include <cstdint>
#include <optional>

namespace embedded::power {

struct BatteryPulsePredictor {
    uint32_t esrMilliohm;
    uint16_t uvloThresholdMilliVolts;

    [[nodiscard]] constexpr std::optional<uint16_t> predictVoltage(uint16_t ocvMilliVolts, uint32_t pulseCurrentMicroAmps) const noexcept {
        const uint32_t sagMilliVolts = (static_cast<uint64_t>(pulseCurrentMicroAmps) * esrMilliohm) / 1000000ULL;
        if (ocvMilliVolts <= sagMilliVolts) {
            return std::nullopt;
        }
        return static_cast<uint16_t>(ocvMilliVolts - sagMilliVolts);
    }

    [[nodiscard]] constexpr bool isSafe(uint16_t ocvMilliVolts, uint32_t pulseCurrentMicroAmps, uint16_t marginMilliVolts = 100) const noexcept {
        const auto vterm = predictVoltage(ocvMilliVolts, pulseCurrentMicroAmps);
        return vterm.has_value() && (*vterm >= (uvloThresholdMilliVolts + marginMilliVolts));
    }
};

} // namespace embedded::power
