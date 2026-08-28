#include <cstdint>
#include <chrono>
#include <concepts>

enum class SafetyState : uint8_t {
    SafeDisarmed,
    Armed,
    TrippedEstop,
    TrippedDeadman,
    FaultCrossCircuit,
    FaultShortPower,
    FaultDiscordance,
    FaultEdm
};

enum class DeadmanPosition : uint8_t {
    Released = 0,
    Enabled  = 1,
    Panic    = 2
};

template <typename HardwareDriver>
class SafetySystem {
public:
    using Milliseconds = std::chrono::milliseconds;
    using Microseconds = std::chrono::microseconds;

    static constexpr Milliseconds PulsePeriod{20};
    static constexpr Microseconds PulseDuration{300};
    static constexpr Milliseconds DiscrepancyLimit{100};
    static constexpr Milliseconds VigilanceLimit{30000};
    static constexpr Milliseconds VigilanceWarnLimit{3000};

    explicit SafetySystem(HardwareDriver& hw)
        : hw_{hw}
    {
        hw_.setTestPulse(1, true);
        hw_.setTestPulse(2, true);
        hw_.setPowerRelays(false);
    }

    void process(DeadmanPosition rawDeadman, bool resetRequested, Milliseconds deltaTime) {
        pulseTimer_ += deltaTime;
        if (pulseTimer_ >= PulsePeriod) {
            pulseTimer_ = Milliseconds{0};
            if (!performPulseTest()) {
                disarm();
                return;
            }
        }

        const bool ch1 = hw_.readInput(1);
        const bool ch2 = hw_.readInput(2);

        // Контроль розбіжності сигналів подвійного каналу E-Stop
        if (ch1 != ch2) {
            if (!discordanceActive_) {
                discordanceActive_ = true;
                discrepancyTimer_ = Milliseconds{0};
            } else {
                discrepancyTimer_ += deltaTime;
                if (discrepancyTimer_ > DiscrepancyLimit) {
                    state_ = SafetyState::FaultDiscordance;
                    disarm();
                    return;
                }
            }
        } else {
            discordanceActive_ = false;
            discrepancyTimer_ = Milliseconds{0};
        }

        const bool estopValid = (ch1 && ch2 && !discordanceActive_);

        // Обробка кінематики мертвої руки за IEC 60947-5-8
        updateDeadmanLogic(rawDeadman, deltaTime);

        // Кінцевий автомат станів
        switch (state_) {
            case SafetyState::SafeDisarmed:
            case SafetyState::TrippedEstop:
            case SafetyState::TrippedDeadman:
                if (!estopValid) {
                    state_ = SafetyState::TrippedEstop;
                } else if (deadmanState_ != DeadmanPosition::Enabled) {
                    state_ = SafetyState::TrippedDeadman;
                } else if (resetRequested) {
                    if (hw_.readEdmFeedback()) {
                        state_ = SafetyState::Armed;
                        hw_.setPowerRelays(true);
                    } else {
                        state_ = SafetyState::FaultEdm;
                    }
                }
                break;

            case SafetyState::Armed:
                if (!estopValid) {
                    state_ = SafetyState::TrippedEstop;
                    disarm();
                } else if (deadmanState_ != DeadmanPosition::Enabled) {
                    state_ = SafetyState::TrippedDeadman;
                    disarm();
                }
                break;

            case SafetyState::FaultCrossCircuit:
            case SafetyState::FaultShortPower:
            case SafetyState::FaultDiscordance:
            case SafetyState::FaultEdm:
                disarm();
                break;
        }
    }

    [[nodiscard]] SafetyState state() const noexcept { return state_; }
    [[nodiscard]] bool isArmed() const noexcept { return state_ == SafetyState::Armed; }
    [[nodiscard]] bool isVigilanceWarning() const noexcept { return vigilanceWarning_; }

private:
    void disarm() noexcept {
        hw_.setPowerRelays(false);
    }

    bool performPulseTest() {
        // Канал 1
        hw_.setTestPulse(1, false);
        hw_.delayUs(PulseDuration.count());
        const bool ch1T1Low = hw_.readInput(1);
        const bool ch2T1Low = hw_.readInput(2);
        hw_.setTestPulse(1, true);

        if (ch1T1Low) {
            state_ = SafetyState::FaultShortPower;
            return false;
        }
        if (!ch2T1Low) {
            state_ = SafetyState::FaultCrossCircuit;
            return false;
        }

        hw_.delayUs(100);

        // Канал 2 (зсув фази)
        hw_.setTestPulse(2, false);
        hw_.delayUs(PulseDuration.count());
        const bool ch1T2Low = hw_.readInput(1);
        const bool ch2T2Low = hw_.readInput(2);
        hw_.setTestPulse(2, true);

        if (ch2T2Low) {
            state_ = SafetyState::FaultShortPower;
            return false;
        }
        if (!ch1T2Low) {
            state_ = SafetyState::FaultCrossCircuit;
            return false;
        }

        return true;
    }

    void updateDeadmanLogic(DeadmanPosition rawPos, Milliseconds dt) {
        if (rawPos == DeadmanPosition::Panic) {
            panicLatch_ = true;
            deadmanState_ = DeadmanPosition::Panic;
        } else if (rawPos == DeadmanPosition::Released) {
            panicLatch_ = false;
            deadmanState_ = DeadmanPosition::Released;
        } else if (rawPos == DeadmanPosition::Enabled) {
            deadmanState_ = panicLatch_ ? DeadmanPosition::Panic : DeadmanPosition::Enabled;
        }

        if (deadmanState_ == DeadmanPosition::Enabled) {
            vigilanceTimer_ += dt;
            if (vigilanceTimer_ >= VigilanceLimit) {
                state_ = SafetyState::TrippedDeadman;
                disarm();
            } else {
                vigilanceWarning_ = (vigilanceTimer_ >= (VigilanceLimit - VigilanceWarnLimit));
            }
        } else {
            vigilanceTimer_ = Milliseconds{0};
            vigilanceWarning_ = false;
        }
    }

    HardwareDriver& hw_;
    SafetyState state_{SafetyState::SafeDisarmed};
    DeadmanPosition deadmanState_{DeadmanPosition::Released};
    bool panicLatch_{false};
    bool discordanceActive_{false};
    bool vigilanceWarning_{false};

    Milliseconds pulseTimer_{0};
    Milliseconds discrepancyTimer_{0};
    Milliseconds vigilanceTimer_{0};
};
