#include <cstdint>
#include <algorithm>

namespace hw {

class EncoderAcceleration {
public:
    static constexpr uint32_t FastThresholdMs = 20;
    static constexpr uint32_t MedThresholdMs  = 50;
    static constexpr uint32_t SlowThresholdMs = 100;

    [[nodiscard]] static constexpr int32_t calculateStep(uint32_t deltaTimeMs, int32_t direction) noexcept {
        int32_t multiplier = 1;
        if (deltaTimeMs < FastThresholdMs) {
            multiplier = 20;
        } else if (deltaTimeMs < MedThresholdMs) {
            multiplier = 5;
        } else if (deltaTimeMs < SlowThresholdMs) {
            multiplier = 2;
        }
        return direction * multiplier;
    }
};

} // namespace hw
