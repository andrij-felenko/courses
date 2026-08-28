/* GasProcessor.hpp — Сучасний, типізований C++20 модуль аналітики газового тракту */
#pragma once

#include <cstdint>
#include <array>
#include <cmath>
#include <optional>
#include <algorithm>

namespace embedded::sensing {

enum class SensorState : std::uint8_t {
    Uninitialized,
    Warmup,
    ReadyValid,
    Fault
};

struct CalibrationConfig {
    float rRefCleanAir{50000.0F}; // Опір у чистому повітрі за 25 °C, 10 г/м³ (Ом)
    float alphaTemp{-0.010F};     // Температурний коефіцієнт (1/K)
    float betaHumidity{0.035F};   // Коефіцієнт абсолютної вологості (м³/г)
    float abcOffsetPpm{0.0F};     // Зсув нуля за алгоритмом ABC (ppm)
};

struct GasMeasurement {
    float concentrationPpm{0.0F};
    float compensatedResistance{0.0F};
    float absoluteHumidityGm3{0.0F};
};

template <std::size_t WindowDays = 7>
class GasSensorEngine {
public:
    static constexpr std::uint32_t WarmupDurationSec = 30U;
    static constexpr std::size_t TotalHourlyBuckets = WindowDays * 24U;
    static constexpr float TargetCleanAirPpm = 400.0F;
    static constexpr float MaxAbcStepPpm = 25.0F;

    explicit GasSensorEngine(CalibrationConfig config = {}, bool enableAbc = true) noexcept
        : config_(config), abcEnabled_(enableAbc)
    {
        hourlyMinHistory_.fill(1e6F);
    }

    void tick1Hz() noexcept
    {
        ++uptimeSec_;

        if (state_ == SensorState::Warmup && uptimeSec_ >= WarmupDurationSec) {
            state_ = SensorState::ReadyValid;
        }

        if (uptimeSec_ % 3600U == 0U && state_ == SensorState::ReadyValid) {
            rotateHourlyBucket();
        }
    }

    [[nodiscard]] std::optional<GasMeasurement> process(float rawResistanceOhms,
                                                         float temperatureC,
                                                         float relativeHumidityPct) noexcept
    {
        if (rawResistanceOhms <= 10.0F) {
            state_ = SensorState::Fault;
            return std::nullopt;
        }

        const float ah = computeAbsoluteHumidity(temperatureC, relativeHumidityPct);
        const float kEnv = std::max(0.2F, 1.0F + config_.alphaTemp * (temperatureC - 25.0F)
                                               + config_.betaHumidity * (ah - 10.0F));

        const float compResistance = rawResistanceOhms * kEnv;

        if (state_ != SensorState::ReadyValid) {
            return std::nullopt; // Під час прогріву дані заблоковані
        }

        float ratio = std::max(0.01F, compResistance / config_.rRefCleanAir);
        float rawPpm = 400.0F * std::pow(ratio, -1.45F);
        float finalPpm = std::max(1.0F, rawPpm - config_.abcOffsetPpm);

        currentHourMinPpm_ = std::min(currentHourMinPpm_, finalPpm);
        ++currentHourSamples_;

        return GasMeasurement{
            .concentrationPpm = finalPpm,
            .compensatedResistance = compResistance,
            .absoluteHumidityGm3 = ah
        };
    }

    void setManualCalibration(float referencePpm, float measuredRawResistance) noexcept
    {
        if (referencePpm > 0.0F && measuredRawResistance > 0.0F) {
            float ratioTarget = std::pow(referencePpm / 400.0F, 1.0F / -1.45F);
            config_.rRefCleanAir = measuredRawResistance / ratioTarget;
            config_.abcOffsetPpm = 0.0F;
        }
    }

    [[nodiscard]] SensorState state() const noexcept { return state_; }
    [[nodiscard]] const CalibrationConfig& config() const noexcept { return config_; }

private:
    [[nodiscard]] static float computeAbsoluteHumidity(float tempC, float rhPct) noexcept
    {
        const float clampedRh = std::clamp(rhPct, 0.0F, 100.0F);
        const float pSat = 6.112F * std::exp((17.62F * tempC) / (243.12F + tempC));
        const float pV = pSat * (clampedRh / 100.0F);
        return (216.7F * pV) / (tempC + 273.15F);
    }

    void rotateHourlyBucket() noexcept
    {
        if (currentHourSamples_ > 0U) {
            hourlyMinHistory_[bucketIndex_] = currentHourMinPpm_;
            bucketIndex_ = (bucketIndex_ + 1U) % TotalHourlyBuckets;
            if (bucketIndex_ == 0U) {
                historyFull_ = true;
                evaluateAbcCorrection();
            }
        }
        currentHourMinPpm_ = 1e6F;
        currentHourSamples_ = 0U;
    }

    void evaluateAbcCorrection() noexcept
    {
        if (!abcEnabled_ || !historyFull_) return;

        const float globalMin = *std::min_element(hourlyMinHistory_.begin(), hourlyMinHistory_.end());
        if (globalMin >= 250.0F && globalMin <= 1200.0F) {
            float delta = globalMin - TargetCleanAirPpm;
            delta = std::clamp(delta, -MaxAbcStepPpm, MaxAbcStepPpm);
            config_.abcOffsetPpm += delta;
        }
    }

    CalibrationConfig config_;
    SensorState state_{SensorState::Warmup};
    bool abcEnabled_{true};
    bool historyFull_{false};
    std::uint32_t uptimeSec_{0U};
    std::size_t bucketIndex_{0U};
    std::uint32_t currentHourSamples_{0U};
    float currentHourMinPpm_{1e6F};
    std::array<float, TotalHourlyBuckets> hourlyMinHistory_{};
};

} // namespace embedded::sensing
