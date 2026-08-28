/* LoadTester.hpp - Idiomatic C++20 implementation */
#pragma once

#include <cstdint>
#include <chrono>
#include <string_view>
#include <concepts>
#include <array>

namespace EmbeddedPower {

using namespace std::chrono_literals;

enum class LoadMode : uint8_t {
    ConstantCurrent,
    ConstantResistance,
    ConstantPower,
    PulsedRadio
};

enum class TesterState : uint8_t {
    Idle,
    Discharging,
    MeasuringIrStep,
    CutoffReached,
    ThermalFault
};

struct TestProfile {
    LoadMode mode{LoadMode::ConstantCurrent};
    uint32_t setpointValue{500};     // mA, mOhm, or mW
    uint32_t pulseHighMa{200};
    uint32_t pulseLowMa{1};
    std::chrono::milliseconds pulseHighDuration{30ms};
    std::chrono::milliseconds pulsePeriod{1000ms};
    uint32_t cutoffMv{3000};
    uint32_t maxHeatsinkTempC{75};
};

struct MeasurementSample {
    uint32_t cellVoltageMv{0};
    uint32_t loadCurrentMa{0};
    uint32_t heatsinkTempC{0};
};

template <typename HardwareDriver>
class ElectronicLoadController {
public:
    explicit constexpr ElectronicLoadController(HardwareDriver& driver, TestProfile profile) noexcept
        : driver_{driver}, profile_{profile} {}

    void start() noexcept {
        state_ = TesterState::Discharging;
        microampSeconds_ = 0;
        microwattSeconds_ = 0;
        elapsedTime_ = 0ms;
        irTimer_ = 0ms;
    }

    void stop() noexcept {
        state_ = TesterState::Idle;
        driver_.setOutputCurrent(0);
    }

    void update(std::chrono::milliseconds dt) noexcept {
        const auto sample = driver_.readSensors();
        currentSample_ = sample;

        if (state_ != TesterState::Discharging && state_ != TesterState::MeasuringIrStep) {
            driver_.setOutputCurrent(0);
            return;
        }

        // Safety supervision
        if (sample.heatsinkTempC >= profile_.maxHeatsinkTempC) {
            driver_.setOutputCurrent(0);
            state_ = TesterState::ThermalFault;
            return;
        }

        if (sample.cellVoltageMv <= profile_.cutoffMv && sample.cellVoltageMv > 200) {
            driver_.setOutputCurrent(0);
            state_ = TesterState::CutoffReached;
            return;
        }

        // Periodic Dynamic DC IR sampling (every 30 seconds)
        irTimer_ += dt;
        if (state_ == TesterState::Discharging && irTimer_ >= 30s) {
            state_ = TesterState::MeasuringIrStep;
            irBaselineVoltageMv_ = sample.cellVoltageMv;
            irBaselineCurrentMa_ = sample.loadCurrentMa;
            driver_.setOutputCurrent(sample.loadCurrentMa + 200);
            return;
        }

        if (state_ == TesterState::MeasuringIrStep) {
            if (irTimer_ >= 30s + 100ms) {
                const auto deltaV = static_cast<int32_t>(irBaselineVoltageMv_) - static_cast<int32_t>(sample.cellVoltageMv);
                const auto deltaI = static_cast<int32_t>(sample.loadCurrentMa) - static_cast<int32_t>(irBaselineCurrentMa_);
                if (deltaI > 50 && deltaV > 0) {
                    lastDcIrMohm_ = static_cast<uint32_t>((deltaV * 1000) / deltaI);
                }
                irTimer_ = 0ms;
                state_ = TesterState::Discharging;
            } else {
                return; // Hold pulse
            }
        }

        // Calculate target current
        const uint32_t targetMa = calculateSetpointCurrent(sample.cellVoltageMv);
        driver_.setOutputCurrent(targetMa);

        // Numerical integration
        microampSeconds_ += static_cast<uint64_t>(sample.loadCurrentMa) * 1000ULL * dt.count() / 1000ULL;
        const uint32_t powerMw = (sample.cellVoltageMv * sample.loadCurrentMa) / 1000UL;
        microwattSeconds_ += static_cast<uint64_t>(powerMw) * 1000ULL * dt.count() / 1000ULL;

        elapsedTime_ += dt;
    }

    [[nodiscard]] constexpr TesterState state() const noexcept { return state_; }
    [[nodiscard]] constexpr uint32_t capacityMah() const noexcept { return static_cast<uint32_t>(microampSeconds_ / 3600000ULL); }
    [[nodiscard]] constexpr uint32_t energyMwh() const noexcept { return static_cast<uint32_t>(microwattSeconds_ / 3600000ULL); }
    [[nodiscard]] constexpr uint32_t dynamicEsrMohm() const noexcept { return lastDcIrMohm_; }

private:
    [[nodiscard]] uint32_t calculateSetpointCurrent(uint32_t vCellMv) const noexcept {
        switch (profile_.mode) {
            case LoadMode::ConstantCurrent:
                return profile_.setpointValue;
            case LoadMode::ConstantResistance:
                return (profile_.setpointValue > 0) ? (vCellMv * 1000UL) / profile_.setpointValue : 0;
            case LoadMode::ConstantPower:
                return (vCellMv >= 500) ? (profile_.setpointValue * 1000UL) / vCellMv : 0;
            case LoadMode::PulsedRadio: {
                const auto phase = elapsedTime_ % profile_.pulsePeriod;
                return (phase < profile_.pulseHighDuration) ? profile_.pulseHighMa : profile_.pulseLowMa;
            }
        }
        return 0;
    }

    HardwareDriver& driver_;
    TestProfile profile_;
    TesterState state_{TesterState::Idle};
    MeasurementSample currentSample_{};

    uint64_t microampSeconds_{0};
    uint64_t microwattSeconds_{0};
    std::chrono::milliseconds elapsedTime_{0ms};
    std::chrono::milliseconds irTimer_{0ms};

    uint32_t irBaselineVoltageMv_{0};
    uint32_t irBaselineCurrentMa_{0};
    uint32_t lastDcIrMohm_{0};
};

} // namespace EmbeddedPower
