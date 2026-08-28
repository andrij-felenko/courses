#include <cstdint>
#include <cmath>
#include <numbers>
#include <span>
#include <algorithm>

namespace sensing {

enum class SensorType {
    CurrentTransformer,
    RogowskiCoil
};

struct SensorConfig {
    SensorType type{SensorType::CurrentTransformer};
    float sampleRateHz{10000.0f};
    float vrefVolts{3.3f};
    uint32_t adcMaxCounts{4095};

    // Параметри CT
    float ctTurnsRatio{2000.0f};
    float ctBurdenResistorOhms{33.0f};
    float ctPhaseOffsetDeg{0.5f};

    // Параметри Rogowski
    float rogowskiMutualInductanceH{1.2e-7f};
    float rogowskiAnalogGain{50.0f};
    float rogowskiLeakyLambda{0.9992f};
};

struct PowerMetrics {
    float iRmsAmperes{0.0f};
    float vRmsVolts{0.0f};
    float activePowerWatts{0.0f};
    float apparentPowerVa{0.0f};
    float powerFactor{1.0f};
};

class CurrentSenseChannel {
public:
    explicit CurrentSenseChannel(const SensorConfig& config) noexcept
        : config_(config) {
        reset();
    }

    void reset() noexcept {
        const float dt = 1.0f / config_.sampleRateHz;
        constexpr float cutoffHz = 0.5f;
        const float rc = 1.0f / (2.0f * std::numbers::pi_v<float> * cutoffHz);
        dcFilterAlpha_ = rc / (rc + dt);

        dcFilterXPrev_ = 0.0f;
        dcFilterYPrev_ = 0.0f;
        integratorState_ = 0.0f;
        integratorXPrev_ = 0.0f;

        sumISquared_ = 0.0f;
        sumVSquared_ = 0.0f;
        sumActivePower_ = 0.0f;
        sampleCount_ = 0;
        metrics_ = {};
    }

    // Обробка поодинокого виміру
    void processSample(uint32_t rawAdcI, float instantVoltageV) noexcept {
        const float vAdc = (static_cast<float>(rawAdcI) / static_cast<float>(config_.adcMaxCounts)) * config_.vrefVolts;

        // IIR DC-Blocker
        const float xAc = vAdc - dcFilterXPrev_ + dcFilterAlpha_ * dcFilterYPrev_;
        dcFilterXPrev_ = vAdc;
        dcFilterYPrev_ = xAc;

        float currentA = 0.0f;

        if (config_.type == SensorType::CurrentTransformer) {
            const float iSec = xAc / config_.ctBurdenResistorOhms;
            currentA = iSec * config_.ctTurnsRatio;
        } else {
            const float dt = 1.0f / config_.sampleRateHz;
            integratorState_ = (config_.rogowskiLeakyLambda * integratorState_) +
                               (0.5f * dt * (xAc + integratorXPrev_));
            integratorXPrev_ = xAc;

            const float totalGain = config_.rogowskiMutualInductanceH * config_.rogowskiAnalogGain;
            if (totalGain > 1e-12f) {
                currentA = integratorState_ / totalGain;
            }
        }

        sumISquared_ += currentA * currentA;
        sumVSquared_ += instantVoltageV * instantVoltageV;
        sumActivePower_ += instantVoltageV * currentA;
        ++sampleCount_;

        constexpr uint32_t windowSize = 200;
        if (sampleCount_ >= windowSize) {
            updateMetrics(windowSize);
        }
    }

    // Пакетна обробка буфера
    void processBatch(std::span<const uint32_t> rawAdcBuffer, std::span<const float> voltageBuffer) noexcept {
        const size_t n = std::min(rawAdcBuffer.size(), voltageBuffer.size());
        for (size_t i = 0; i < n; ++i) {
            processSample(rawAdcBuffer[i], voltageBuffer[i]);
        }
    }

    [[nodiscard]] const PowerMetrics& metrics() const noexcept {
        return metrics_;
    }

private:
    void updateMetrics(uint32_t windowSize) noexcept {
        const float invN = 1.0f / static_cast<float>(windowSize);

        metrics_.iRmsAmperes = std::sqrt(sumISquared_ * invN);
        metrics_.vRmsVolts = std::sqrt(sumVSquared_ * invN);
        metrics_.activePowerWatts = sumActivePower_ * invN;
        metrics_.apparentPowerVa = metrics_.vRmsVolts * metrics_.iRmsAmperes;

        if (metrics_.apparentPowerVa > 1e-3f) {
            metrics_.powerFactor = std::clamp(metrics_.activePowerWatts / metrics_.apparentPowerVa, -1.0f, 1.0f);
        } else {
            metrics_.powerFactor = 1.0f;
        }

        sumISquared_ = 0.0f;
        sumVSquared_ = 0.0f;
        sumActivePower_ = 0.0f;
        sampleCount_ = 0;
    }

    SensorConfig config_;
    float dcFilterAlpha_{0.999f};
    float dcFilterXPrev_{0.0f};
    float dcFilterYPrev_{0.0f};
    float integratorState_{0.0f};
    float integratorXPrev_{0.0f};

    float sumISquared_{0.0f};
    float sumVSquared_{0.0f};
    float sumActivePower_{0.0f};
    uint32_t sampleCount_{0};

    PowerMetrics metrics_{};
};

} // namespace sensing
