#include <optional>
#include <cmath>

class RvdtRatiometricCalculator {
public:
    static constexpr float kSumMinVolts = 0.1f;
    static constexpr float kScaleRad = 0.7853f;

    struct SignalInput {
        float v_s1;
        float v_s2;
    };

    static std::optional<float> calculateRawAngle(const SignalInput& input) noexcept {
        const float sum = input.v_s1 + input.v_s2;
        if (sum < kSumMinVolts) {
            return std::nullopt; // Захист від ділення на нуль та виявлення обриву
        }
        const float diff = input.v_s1 - input.v_s2;
        const float m_raw = diff / sum;
        return m_raw * kScaleRad;
    }
};
