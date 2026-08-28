#include <chrono>
#include <algorithm>
#include <cstdint>
#include <optional>
#include <span>

using namespace std::chrono_literals;

class FallbackController {
public:
    enum class State : uint8_t {
        Online,
        HoldPhase1,
        AutonomousPhase2,
        SafeStatePhase3,
        Reconnecting
    };

    struct ControlCommand {
        float throttle{0.0f};  // діапазон [-1.0f .. +1.0f]
        float steering{0.0f};  // діапазон [-1.0f .. +1.0f]
        uint32_t sequenceId{0};
    };

    explicit FallbackController(std::chrono::milliseconds deadmanTimeout = 250ms,
                                std::chrono::milliseconds phase1Timeout = 5000ms,
                                std::chrono::milliseconds phase2Timeout = 60000ms)
        : deadmanTimeout_{deadmanTimeout},
          phase1Timeout_{phase1Timeout},
          phase2Timeout_{phase2Timeout} {}

    void onPacketReceived(const ControlCommand& cmd, std::chrono::milliseconds now) noexcept {
        lastPacketTime_ = now;
        cachedCmd_ = cmd;

        if (state_ == State::HoldPhase1) {
            state_ = State::Online;
        } else if (state_ == State::AutonomousPhase2 || state_ == State::SafeStatePhase3) {
            state_ = State::Reconnecting;
            stateEntryTime_ = now;
            logEvent(0xA1, now);
        }
    }

    void update(std::chrono::milliseconds now) noexcept {
        const auto silenceDuration = now - lastPacketTime_;

        switch (state_) {
            case State::Online:
                if (silenceDuration > deadmanTimeout_) {
                    state_ = State::HoldPhase1;
                    stateEntryTime_ = now;
                    logEvent(0x01, now);
                } else {
                    currentThrottle_ = cachedCmd_.throttle;
                    currentSteering_ = cachedCmd_.steering;
                    applyActuators(currentThrottle_, currentSteering_);
                }
                break;

            case State::HoldPhase1:
                if (silenceDuration > phase1Timeout_) {
                    state_ = State::AutonomousPhase2;
                    stateEntryTime_ = now;
                    logEvent(0x02, now);
                } else {
                    // Утримання уставки з безпечним обмеженням тяги
                    currentThrottle_ = cachedCmd_.throttle * 0.8f;
                    currentSteering_ = cachedCmd_.steering;
                    applyActuators(currentThrottle_, currentSteering_);
                }
                break;

            case State::AutonomousPhase2:
                if (silenceDuration > phase2Timeout_) {
                    state_ = State::SafeStatePhase3;
                    stateEntryTime_ = now;
                    setPowerStageEnabled(false); // Апаратне знеструмлення
                    currentThrottle_ = 0.0f;
                    currentSteering_ = 0.0f;
                    applyActuators(0.0f, 0.0f);
                    logEvent(0x03, now);
                } else {
                    // Локальна евристика: плавне зниження швидкості
                    currentThrottle_ = std::max(0.0f, currentThrottle_ - 0.02f);
                    currentSteering_ = 0.0f;
                    applyActuators(currentThrottle_, currentSteering_);
                }
                break;

            case State::SafeStatePhase3:
                applyActuators(0.0f, 0.0f);
                break;

            case State::Reconnecting:
                setPowerStageEnabled(true);
                // Плавне наростання (Ramp) без механічного ривка
                const float step = 0.05f;
                const float delta = cachedCmd_.throttle - currentThrottle_;
                if (delta > step) currentThrottle_ += step;
                else if (delta < -step) currentThrottle_ -= step;
                else currentThrottle_ = cachedCmd_.throttle;

                currentSteering_ = cachedCmd_.steering;
                applyActuators(currentThrottle_, currentSteering_);

                if ((now - stateEntryTime_) > 1000ms) {
                    state_ = State::Online;
                    logEvent(0xA2, now);
                }
                break;
        }
    }

    [[nodiscard]] State currentState() const noexcept { return state_; }
    [[nodiscard]] bool isPowerEnabled() const noexcept { return powerEnabled_; }

private:
    void applyActuators(float throttle, float steering) noexcept {
        // Запис у регістри таймерів ШІМ силового каскаду
    }

    void setPowerStageEnabled(bool enable) noexcept {
        powerEnabled_ = enable;
        // Керування апаратною лінією Gate Kill / Enable
    }

    void logEvent(uint8_t eventCode, std::chrono::milliseconds timestamp) noexcept {
        // Неблокуючий запис у кільцевий буфер Flash/FRAM
    }

    const std::chrono::milliseconds deadmanTimeout_;
    const std::chrono::milliseconds phase1Timeout_;
    const std::chrono::milliseconds phase2Timeout_;

    State state_{State::Online};
    std::chrono::milliseconds lastPacketTime_{0ms};
    std::chrono::milliseconds stateEntryTime_{0ms};
    ControlCommand cachedCmd_{};

    float currentThrottle_{0.0f};
    float currentSteering_{0.0f};
    bool powerEnabled_{true};
};
