#include <cstdint>
#include <cmath>
#include <array>
#include <chrono>

namespace drone::safety {

enum class PtuState : uint8_t {
    Disarmed = 0,
    Armed,
    FreefallConfirming,
    TumbleConfirming,
    MotorCutoffActive,
    IgnitionActive,
    Deployed
};

struct ImuVector3 {
    float x{0.0f};
    float y{0.0f};
    float z{0.0f};

    [[nodiscard]] float magnitude() const noexcept {
        return std::sqrt(x * x + y * y + z * z);
    }
};

struct ImuSample {
    ImuVector3 accel_mss;  // м/с^2
    ImuVector3 gyro_dps;   // град/с
};

class ParachuteTriggerUnit {
public:
    static constexpr float FreefallThresholdG = 0.22f;
    static constexpr float TumbleThresholdDps = 380.0f;
    static constexpr uint32_t ConfirmTimeMs = 90;
    static constexpr uint32_t SpindownDelayMs = 50;
    static constexpr uint32_t IgniterPulseDurationMs = 200;
    static constexpr float GravityMss = 9.80665f;
    static constexpr float FilterAlpha = 0.30f;

    ParachuteTriggerUnit() noexcept = default;

    void setArmed(bool armed, uint32_t currentTimeMs) noexcept {
        if (state_ == PtuState::Deployed || state_ >= PtuState::MotorCutoffActive) {
            return; // Захист від скидання під час аварійного циклу
        }
        state_ = armed ? PtuState::Armed : PtuState::Disarmed;
        stateEntryTimeMs_ = currentTimeMs;
    }

    void update(const ImuSample& imu, uint32_t currentTimeMs) noexcept {
        const float currentAccelG = imu.accel_mss.magnitude() / GravityMss;
        const float currentGyroDps = imu.gyro_dps.magnitude();

        // Експоненційний фільтр зрізання вібрацій
        filteredAccelG_ = FilterAlpha * currentAccelG + (1.0f - FilterAlpha) * filteredAccelG_;
        filteredGyroDps_ = FilterAlpha * currentGyroDps + (1.0f - FilterAlpha) * filteredGyroDps_;

        const bool isFreefall = (filteredAccelG_ < FreefallThresholdG);
        const bool isTumble = (filteredGyroDps_ > TumbleThresholdDps);

        switch (state_) {
            case PtuState::Disarmed:
                break;

            case PtuState::Armed:
                if (isFreefall) {
                    state_ = PtuState::FreefallConfirming;
                    anomalyStartTimeMs_ = currentTimeMs;
                } else if (isTumble) {
                    state_ = PtuState::TumbleConfirming;
                    anomalyStartTimeMs_ = currentTimeMs;
                }
                break;

            case PtuState::FreefallConfirming:
                if (!isFreefall) {
                    state_ = PtuState::Armed;
                } else if ((currentTimeMs - anomalyStartTimeMs_) >= ConfirmTimeMs) {
                    executeMotorCutoff(currentTimeMs);
                }
                break;

            case PtuState::TumbleConfirming:
                if (!isTumble) {
                    state_ = PtuState::Armed;
                } else if ((currentTimeMs - anomalyStartTimeMs_) >= ConfirmTimeMs) {
                    executeMotorCutoff(currentTimeMs);
                }
                break;

            case PtuState::MotorCutoffActive:
                if ((currentTimeMs - stateEntryTimeMs_) >= SpindownDelayMs) {
                    executeIgnition(currentTimeMs);
                }
                break;

            case PtuState::IgnitionActive:
                if ((currentTimeMs - stateEntryTimeMs_) >= IgniterPulseDurationMs) {
                    hardwareSetIgniter(false);
                    state_ = PtuState::Deployed;
                    stateEntryTimeMs_ = currentTimeMs;
                }
                break;

            case PtuState::Deployed:
                hardwareSetFtsCutoff(true);
                break;
        }
    }

    [[nodiscard]] PtuState state() const noexcept { return state_; }
    [[nodiscard]] bool isFtsEngaged() const noexcept { return ftsEngaged_; }
    [[nodiscard]] bool isIgniterFired() const noexcept { return igniterFired_; }

private:
    void executeMotorCutoff(uint32_t now) noexcept {
        state_ = PtuState::MotorCutoffActive;
        stateEntryTimeMs_ = now;
        ftsEngaged_ = true;
        hardwareSetFtsCutoff(true);
    }

    void executeIgnition(uint32_t now) noexcept {
        state_ = PtuState::IgnitionActive;
        stateEntryTimeMs_ = now;
        igniterFired_ = true;
        hardwareSetIgniter(true);
    }

    // Апаратні заглушки взаємодії з драйверами
    static void hardwareSetFtsCutoff(bool disableMotors) noexcept {
        // Запис у регістр GPIO / SPI переривача DShot
    }

    static void hardwareSetIgniter(bool enablePower) noexcept {
        // Керування польовим MOSFET-ключем підпалу піропатрона
    }

    PtuState state_{PtuState::Disarmed};
    uint32_t stateEntryTimeMs_{0};
    uint32_t anomalyStartTimeMs_{0};
    float filteredAccelG_{1.0f};
    float filteredGyroDps_{0.0f};
    bool ftsEngaged_{false};
    bool igniterFired_{false};
};

} // namespace drone::safety
