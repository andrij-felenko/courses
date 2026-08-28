#include <array>
#include <algorithm>
#include <cstdint>
#include <span>

class ThermalManager {
public:
    enum class State : uint8_t {
        Normal = 0,
        Warming,
        Throttled,
        Critical,
        Shutdown
    };

    struct SensorConfig {
        float limitWarn{60.0f};
        float limitCrit{100.0f};
    };

    struct SensorState {
        float currentTemp{25.0f};
        float prevTemp{25.0f};
        float slewRate{0.0f};
        SensorConfig config{};

        void update(float newTemp, float dtSec) noexcept {
            if (dtSec > 0.001f) {
                slewRate = (newTemp - prevTemp) / dtSec;
            }
            prevTemp = currentTemp;
            currentTemp = newTemp;
        }

        [[nodiscard]] float normalizedStress() const noexcept {
            return currentTemp / config.limitCrit;
        }
    };

    struct PiConfig {
        float kp{0.04f};
        float ki{0.01f};
        float targetTemp{72.0f};
        float iMin{-0.80f};
        float iMax{0.0f};
    };

    static constexpr size_t SensorCount = 3;
    static constexpr uint32_t DwellTimeMs = 5000;
    static constexpr float MaxSlewRate = 5.0f; // °C/с

    constexpr ThermalManager() noexcept {
        sensors_[0].config = { .limitWarn = 60.0f, .limitCrit = 100.0f }; // MCU Die
        sensors_[1].config = { .limitWarn = 65.0f, .limitCrit = 90.0f };  // MOSFETs
        sensors_[2].config = { .limitWarn = 45.0f, .limitCrit = 60.0f };  // Battery
    }

    void update(std::span<const float, SensorCount> rawTemps, uint32_t currentTimeMs) noexcept {
        float dtSec = (lastUpdateTimeMs_ == 0) ? 0.05f : static_cast<float>(currentTimeMs - lastUpdateTimeMs_) / 1000.0f;
        if (dtSec <= 0.0f) dtSec = 0.05f;
        lastUpdateTimeMs_ = currentTimeMs;

        float maxStress = 0.0f;
        float maxAbsTemp = 0.0f;
        bool shock = false;

        for (size_t i = 0; i < SensorCount; ++i) {
            sensors_[i].update(rawTemps[i], dtSec);
            maxAbsTemp = std::max(maxAbsTemp, sensors_[i].currentTemp);
            maxStress = std::max(maxStress, sensors_[i].normalizedStress());
            if (sensors_[i].slewRate > MaxSlewRate) {
                shock = true;
            }
        }

        const uint32_t timeInState = currentTimeMs - stateEntryTimeMs_;
        State nextState = state_;

        if (shock || maxStress >= 1.0f) {
            nextState = State::Shutdown;
        } else {
            switch (state_) {
                case State::Normal:
                    if (maxStress >= 0.70f) nextState = State::Warming;
                    throttleFactor_ = 1.0f;
                    iTerm_ = 0.0f;
                    break;

                case State::Warming:
                    if (maxStress >= 0.85f) {
                        nextState = State::Throttled;
                    } else if (maxStress < 0.60f && timeInState >= DwellTimeMs) {
                        nextState = State::Normal;
                    }
                    throttleFactor_ = 1.0f;
                    break;

                case State::Throttled:
                    if (maxStress >= 0.95f) {
                        nextState = State::Critical;
                    } else if (maxStress < 0.75f && timeInState >= DwellTimeMs) {
                        nextState = State::Warming;
                    } else {
                        // ПІ-регулятор обмеження
                        const float err = piConfig_.targetTemp - maxAbsTemp;
                        iTerm_ = std::clamp(iTerm_ + piConfig_.ki * err * dtSec, piConfig_.iMin, piConfig_.iMax);
                        const float rawK = 1.0f + (piConfig_.kp * err + iTerm_);
                        throttleFactor_ = std::clamp(rawK, 0.20f, 1.00f);
                    }
                    break;

                case State::Critical:
                    if (maxStress < 0.85f && timeInState >= DwellTimeMs) {
                        nextState = State::Throttled;
                    }
                    throttleFactor_ = 0.20f;
                    break;

                case State::Shutdown:
                    throttleFactor_ = 0.0f;
                    break;
            }
        }

        if (nextState != state_) {
            state_ = nextState;
            stateEntryTimeMs_ = currentTimeMs;
        }
    }

    [[nodiscard]] State state() const noexcept { return state_; }
    [[nodiscard]] float throttleFactor() const noexcept { return throttleFactor_; }

private:
    State state_{State::Normal};
    std::array<SensorState, SensorCount> sensors_{};
    PiConfig piConfig_{};
    float iTerm_{0.0f};
    float throttleFactor_{1.0f};
    uint32_t stateEntryTimeMs_{0};
    uint32_t lastUpdateTimeMs_{0};
};
