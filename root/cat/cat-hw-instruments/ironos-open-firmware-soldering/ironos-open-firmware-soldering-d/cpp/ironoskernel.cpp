#include <cstdint>
#include <algorithm>

class IronOsKernel {
public:
    static constexpr float AdcMaxRaw = 4095.0f;
    static constexpr float VRef = 3.3f;
    static constexpr float OpAmpGain = 250.0f;
    static constexpr float SeebeckCoeff = 0.000041f;

    struct KernelState {
        float targetTemp{300.0f};
        float currentTemp{25.0f};
        float inputVoltage{20.0f};
        uint16_t pwmDuty{0};
        bool sleepActive{false};
    };

    explicit IronOsKernel(float tipResistance = 8.0f) 
        : tipResistance_(tipResistance) {}

    float calculateTemperature(uint16_t adcRawTc, float coldJunctionTemp) const {
        float vTc = (static_cast<float>(adcRawTc) / AdcMaxRaw) * VRef / OpAmpGain;
        float tUncorrected = vTc / SeebeckCoeff;
        return tUncorrected + coldJunctionTemp;
    }

    void processLoopStep(KernelState& state, uint16_t adcTc, float coldJunc, float measuredVin) {
        state.inputVoltage = measuredVin;
        state.currentTemp = calculateTemperature(adcTc, coldJunc);

        float pMax = (state.inputVoltage * state.inputVoltage) / tipResistance_;
        float pTarget = 30.0f;
        float dMax = (pMax > 0.0f) ? std::min(1.0f, pTarget / pMax) : 0.0f;

        float error = state.targetTemp - state.currentTemp;
        if (error > 0.0f) {
            float dutyRatio = std::min(dMax, error * 0.05f);
            state.pwmDuty = static_cast<uint16_t>(dutyRatio * 1000.0f);
        } else {
            state.pwmDuty = 0;
        }
    }

private:
    float tipResistance_;
};
