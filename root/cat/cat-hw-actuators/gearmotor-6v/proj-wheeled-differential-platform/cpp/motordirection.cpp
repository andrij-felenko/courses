/**
 * @file MotorDriver.hpp
 * @brief Об'єктно-орієнтований драйвер мотор-редуктора з функціоналом Stall Detection.
 */

#pragma once

#include <cstdint>
#include <array>

namespace EmbeddedActuators {

enum class MotorDirection : uint8_t {
    Stop = 0,
    Forward,
    Reverse
};

enum class FsmState : uint8_t {
    Idle = 0,
    Blanking,
    Running,
    Overload,
    Fault
};

/* Апаратний інтерфейс низького рівня */
class IMotorHwBridge {
public:
    virtual ~IMotorHwBridge() = default;
    virtual void setPwmDuty(uint16_t dutyPerMille) noexcept = 0;
    virtual void setDirection(MotorDirection dir) noexcept = 0;
    virtual void engageActiveBrake() noexcept = 0;
};

/* Цифровий фільтр ковзного середнього */
template <std::size_t WindowSize = 8>
class MovingAverageFilter {
    static_assert((WindowSize & (WindowSize - 1)) == 0, "WindowSize мусить бути степенем двійки!");
public:
    MovingAverageFilter() noexcept { reset(); }

    void reset() noexcept {
        buffer_.fill(0);
        accumulator_ = 0;
        head_ = 0;
    }

    uint16_t update(uint16_t sample) noexcept {
        accumulator_ -= buffer_[head_];
        buffer_[head_] = sample;
        accumulator_ += sample;
        head_ = (head_ + 1) & (WindowSize - 1);
        return static_cast<uint16_t>(accumulator_ >> 3); // Бітовий зсув замість ділення на 8
    }

private:
    std::array<uint16_t, WindowSize> buffer_{};
    uint32_t accumulator_{0};
    std::size_t head_{0};
};

/* Монітор струму на основі шунта в нижньому плечі */
class CurrentMonitor {
public:
    constexpr CurrentMonitor(uint16_t shuntMilliOhms, uint16_t vrefMilliVolts) noexcept
        : shuntMilliOhms_(shuntMilliOhms), vrefMilliVolts_(vrefMilliVolts) {}

    uint16_t processSample(uint16_t rawAdc) noexcept {
        uint16_t filteredAdc = filter_.update(rawAdc);
        // Підсумкова формула: I_mA = (ADC * Vref_mV * 1000) / (1023 * Rshunt_mOhm)
        uint32_t numerator = static_cast<uint32_t>(filteredAdc) * vrefMilliVolts_ * 1000U;
        uint32_t denominator = 1023U * shuntMilliOhms_;
        currentMilliAmps_ = static_cast<uint16_t>(numerator / denominator);
        return currentMilliAmps_;
    }

    [[nodiscard]] uint16_t getCurrentMa() const noexcept { return currentMilliAmps_; }
    void reset() noexcept { filter_.reset(); currentMilliAmps_ = 0; }

private:
    uint16_t shuntMilliOhms_;
    uint16_t vrefMilliVolts_;
    uint16_t currentMilliAmps_{0};
    MovingAverageFilter<8> filter_{};
};

/* Клас керування каналом мотора */
class MotorChannel {
public:
    using StallCallback = void (*)(uint8_t channelId, void* context);

    struct ProtectionConfig {
        uint16_t tripCurrentMa{650};       // Поріг струму відсікання
        uint16_t hysteresisMa{50};         // Гістерезис повернення в штатний стан
        uint32_t blankingWindowMs{40};     // Вікно маскування пуску
        uint32_t stallTimeoutMs{120};      // Час підтвердження заклинювання
    };

    MotorChannel(uint8_t channelId, IMotorHwBridge& bridge,
                 CurrentMonitor& monitor, const ProtectionConfig& config) noexcept
        : channelId_(channelId), bridge_(bridge), monitor_(monitor), config_(config) {}

    void registerStallCallback(StallCallback callback, void* context = nullptr) noexcept {
        stallCallback_ = callback;
        callbackContext_ = context;
    }

    void setSpeed(MotorDirection dir, uint16_t dutyPerMille, uint32_t nowMs) noexcept {
        if (state_ == FsmState::Fault) {
            return;
        }

        if (dir == MotorDirection::Stop || dutyPerMille == 0) {
            stop();
            return;
        }

        bool requiresBlanking = (state_ == FsmState::Idle) || (direction_ != dir);

        direction_ = dir;
        targetDuty_ = (dutyPerMille > 1000) ? 1000 : dutyPerMille;

        bridge_.setDirection(direction_);
        bridge_.setPwmDuty(targetDuty_);

        if (requiresBlanking) {
            state_ = FsmState::Blanking;
            stateTimestampMs_ = nowMs;
        }
    }

    void stop() noexcept {
        direction_ = MotorDirection::Stop;
        targetDuty_ = 0;
        state_ = FsmState::Idle;
        bridge_.setPwmDuty(0);
        bridge_.setDirection(MotorDirection::Stop);
    }

    void emergencyBrake() noexcept {
        targetDuty_ = 0;
        direction_ = MotorDirection::Stop;
        state_ = FsmState::Fault;

        bridge_.setPwmDuty(0);
        bridge_.engageActiveBrake();

        if (stallCallback_ != nullptr) {
            stallCallback_(channelId_, callbackContext_);
        }
    }

    bool clearFault() noexcept {
        if (state_ != FsmState::Fault) {
            return false;
        }
        monitor_.reset();
        stop();
        return true;
    }

    void process(uint16_t rawAdc, uint32_t nowMs) noexcept {
        uint16_t currentMa = monitor_.processSample(rawAdc);

        switch (state_) {
        case FsmState::Idle:
            break;

        case FsmState::Blanking:
            if ((nowMs - stateTimestampMs_) >= config_.blankingWindowMs) {
                state_ = FsmState::Running;
            }
            break;

        case FsmState::Running:
            if (currentMa >= config_.tripCurrentMa) {
                state_ = FsmState::Overload;
                overloadStartMs_ = nowMs;
            }
            break;

        case FsmState::Overload:
            if (currentMa < (config_.tripCurrentMa - config_.hysteresisMa)) {
                state_ = FsmState::Running;
            } else if ((nowMs - overloadStartMs_) >= config_.stallTimeoutMs) {
                emergencyBrake();
            }
            break;

        case FsmState::Fault:
            break;
        }
    }

    [[nodiscard]] FsmState getState() const noexcept { return state_; }
    [[nodiscard]] uint16_t getCurrentMa() const noexcept { return monitor_.getCurrentMa(); }

private:
    uint8_t channelId_;
    IMotorHwBridge& bridge_;
    CurrentMonitor& monitor_;
    ProtectionConfig config_;

    FsmState state_{FsmState::Idle};
    MotorDirection direction_{MotorDirection::Stop};
    uint16_t targetDuty_{0};

    uint32_t stateTimestampMs_{0};
    uint32_t overloadStartMs_{0};

    StallCallback stallCallback_{nullptr};
    void* callbackContext_{nullptr};
};

} // namespace EmbeddedActuators
