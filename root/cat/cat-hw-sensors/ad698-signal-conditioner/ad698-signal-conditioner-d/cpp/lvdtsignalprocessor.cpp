#include <cstdint>

class LvdtSignalProcessor {
public:
    struct CalibrationData {
        float gainMmPerVolt{1.0f};
        float zeroOffsetVolts{2.5f};
        float adcVrefVolts{3.3f};
        std::uint32_t adcMaxCodes{4095}; // 12-бітний АЦП
    };

    explicit LvdtSignalProcessor(const CalibrationData& cal) : cal_(cal) {}

    [[nodiscard]] float calculateDisplacementMm(std::uint32_t rawAdcCode) const noexcept {
        if (cal_.adcMaxCodes == 0) {
            return 0.0f;
        }
        const float vMeasured = (static_cast<float>(rawAdcCode) / static_cast<float>(cal_.adcMaxCodes)) * cal_.adcVrefVolts;
        return (vMeasured - cal_.zeroOffsetVolts) * cal_.gainMmPerVolt;
    }

private:
    CalibrationData cal_;
};
