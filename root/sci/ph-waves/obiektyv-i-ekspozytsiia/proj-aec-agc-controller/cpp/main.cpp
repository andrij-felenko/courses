#include <cstdint>
#include <cmath>
#include <array>
#include <span>
#include <algorithm>

namespace vision::isp {

enum class AntiFlickerMode : uint32_t {
    Disabled = 0,
    Mains50Hz = 50,
    Mains60Hz = 60
};

struct ExposureLimits {
    uint32_t minExposureUs{50};
    uint32_t maxExposureUs{33333};
    uint32_t maxMotionExposureUs{8333};
    float minAnalogGain{1.0f};
    float maxAnalogGain{16.0f};
    float minDigitalGain{1.0f};
    float maxDigitalGain{4.0f};
};

struct ExposureSettings {
    uint32_t exposureUs{10000};
    float analogGain{1.0f};
    float digitalGain{1.0f};
};

class AutoExposureController {
public:
    static constexpr size_t GridRows = 8;
    static constexpr size_t GridCols = 8;

    explicit AutoExposureController(const ExposureLimits& limits = ExposureLimits{})
        : limits_(limits) {}

    void setTargetLuminance(float target, float deadband = 3.0f) noexcept {
        targetLuma_ = target;
        deadband_ = deadband;
    }

    void setDampingFactor(float kp) noexcept {
        kp_ = std::clamp(kp, 0.05f, 1.0f);
    }

    void setAntiFlicker(AntiFlickerMode mode) noexcept {
        flickerMode_ = mode;
    }

    [[nodiscard]] const ExposureSettings& currentSettings() const noexcept {
        return current_;
    }

    [[nodiscard]] static float computeWeightedLuminance(
        std::span<const uint8_t, GridRows * GridCols> gridData) noexcept {
        
        static constexpr std::array<uint8_t, GridRows * GridCols> CenterWeights = {
            1,  1,  2,  2,  2,  2,  1,  1,
            1,  2,  4,  4,  4,  4,  2,  1,
            2,  4,  8, 12, 12,  8,  4,  2,
            2,  4, 12, 16, 16, 12,  4,  2,
            2,  4, 12, 16, 16, 12,  4,  2,
            2,  4,  8, 12, 12,  8,  4,  2,
            1,  2,  4,  4,  4,  4,  2,  1,
            1,  1,  2,  2,  2,  2,  1,  1
        };

        uint32_t weightedSum = 0;
        uint32_t totalWeight = 0;

        for (size_t i = 0; i < gridData.size(); ++i) {
            uint32_t w = CenterWeights[i];
            weightedSum += static_cast<uint32_t>(gridData[i]) * w;
            totalWeight += w;
        }

        if (totalWeight == 0) return 1.0f;
        return static_cast<float>(weightedSum) / static_cast<float>(totalWeight);
    }

    bool update(float measuredLuma) noexcept {
        measuredLuma = std::max(measuredLuma, 1.0f);
        float error = targetLuma_ - measuredLuma;

        if (std::abs(error) <= deadband_) {
            return false;
        }

        float lumaRatio = targetLuma_ / measuredLuma;
        float deltaEv = kp_ * std::log2(lumaRatio);
        deltaEv = std::clamp(deltaEv, -1.5f, 1.5f);

        float scale = std::exp2(deltaEv);
        float currentTotal = static_cast<float>(current_.exposureUs) *
                             current_.analogGain * current_.digitalGain;
        float desiredTotal = currentTotal * scale;

        allocateParameters(desiredTotal);
        return true;
    }

private:
    void allocateParameters(float desiredTotal) noexcept {
        uint32_t expUs = limits_.minExposureUs;
        float anaGain = limits_.minAnalogGain;
        float digGain = limits_.minDigitalGain;

        float maxShutterBudget = static_cast<float>(limits_.maxMotionExposureUs) *
                                 limits_.minAnalogGain * limits_.minDigitalGain;

        if (desiredTotal <= maxShutterBudget) {
            expUs = static_cast<uint32_t>(desiredTotal / (limits_.minAnalogGain * limits_.minDigitalGain));
        } else {
            expUs = limits_.maxMotionExposureUs;
            float budget = desiredTotal / static_cast<float>(expUs);

            if (budget <= limits_.maxAnalogGain) {
                anaGain = budget;
            } else {
                anaGain = limits_.maxAnalogGain;
                budget /= anaGain;

                if (budget <= limits_.maxDigitalGain) {
                    digGain = budget;
                } else {
                    digGain = limits_.maxDigitalGain;
                    float remaining = budget / digGain;
                    uint32_t extended = static_cast<uint32_t>(static_cast<float>(expUs) * remaining);
                    expUs = std::min(extended, limits_.maxExposureUs);
                }
            }
        }

        expUs = applyAntiFlicker(expUs);

        current_.exposureUs = std::clamp(expUs, limits_.minExposureUs, limits_.maxExposureUs);
        current_.analogGain = std::clamp(anaGain, limits_.minAnalogGain, limits_.maxAnalogGain);
        current_.digitalGain = std::clamp(digGain, limits_.minDigitalGain, limits_.maxDigitalGain);
    }

    [[nodiscard]] uint32_t applyAntiFlicker(uint32_t expUs) const noexcept {
        if (flickerMode_ == AntiFlickerMode::Disabled) return expUs;

        uint32_t stepUs = (flickerMode_ == AntiFlickerMode::Mains50Hz) ? 10000 : 8333;
        if (expUs < stepUs) return expUs;

        uint32_t steps = (expUs + (stepUs / 2)) / stepUs;
        steps = std::max(steps, 1u);

        uint32_t quantized = steps * stepUs;
        return std::clamp(quantized, limits_.minExposureUs, limits_.maxExposureUs);
    }

    ExposureLimits limits_;
    ExposureSettings current_{};
    float targetLuma_{118.0f};
    float deadband_{3.0f};
    float kp_{0.35f};
    AntiFlickerMode flickerMode_{AntiFlickerMode::Mains50Hz};
};

} // namespace vision::isp
