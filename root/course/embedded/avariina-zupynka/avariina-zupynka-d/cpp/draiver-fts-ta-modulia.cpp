#include <cstdint>
#include <chrono>
#include <array>
#include <span>
#include <concepts>

enum class PlatformType : uint8_t {
    Multicopter,
    FixedWing,
    Rover
};

enum class FtsState : uint8_t {
    Disarmed,
    Armed,
    TerminationTriggered,
    ParachuteDeployed,
    LinkLost
};

template <typename HardwareAbstraction>
concept FtsHardware = requires(HardwareAbstraction hw, bool flag) {
    { hw.getTimeMs() } -> std::same_as<std::chrono::milliseconds>;
    { hw.setPowerSwitch(flag) } -> std::same_as<void>;
    { hw.setParachutePyro(flag) } -> std::same_as<void>;
    { hw.emergencyDisableTimerPwm() } -> std::same_as<void>;
    { hw.setControlSurfacesSpiral() } -> std::same_as<void>;
};

template <FtsHardware Hal>
class FlightTerminationSystem {
public:
    using Milliseconds = std::chrono::milliseconds;

    static constexpr uint8_t MagicByte{0x5A};
    static constexpr uint8_t CmdKillPower{0xA5};
    static constexpr uint8_t CmdArmSystem{0x5A};
    static constexpr Milliseconds HeartbeatTimeout{500};
    static constexpr Milliseconds ParachuteDelay{80};

    explicit FlightTerminationSystem(Hal& hal, PlatformType platform)
        : hal_{hal}, platform_{platform}
    {
        hal_.setPowerSwitch(false);
        hal_.setParachutePyro(false);
        hal_.emergencyDisableTimerPwm();
    }

    void triggerTermination() noexcept {
        if (state_ == FtsState::TerminationTriggered || state_ == FtsState::ParachuteDeployed) {
            return;
        }

        state_ = FtsState::TerminationTriggered;
        terminationTimestamp_ = hal_.getTimeMs();

        // 1. Апаратний розрив силових ключів
        hal_.setPowerSwitch(false);

        // 2. Апаратне вимкнення виходів ШІМ
        hal_.emergencyDisableTimerPwm();

        // 3. Специфічний перехід у безпечний стан для типу планера
        if (platform_ == PlatformType::FixedWing) {
            hal_.setControlSurfacesSpiral();
        }
    }

    void processIncomingPacket(std::span<const uint8_t> packet) noexcept {
        if (packet.size() != 5 || packet[0] != MagicByte) {
            return;
        }

        const uint16_t receivedCrc = static_cast<uint16_t>((static_cast<uint16_t>(packet[3]) << 8) | packet[4]);
        const uint16_t computedCrc = calculateCrc16(packet.subspan(0, 3));

        if (receivedCrc != computedCrc) {
            return;
        }

        lastHeartbeat_ = hal_.getTimeMs();
        const uint8_t command = packet[1];
        const uint8_t auxFlags = packet[2];

        if (command == CmdKillPower) {
            triggerTermination();
        } else if (command == CmdArmSystem && state_ == FtsState::Disarmed) {
            state_ = FtsState::Armed;
            parachuteArmed_ = (auxFlags != 0);
            hal_.setPowerSwitch(true);
        }
    }

    void updatePeriodic() noexcept {
        const auto now = hal_.getTimeMs();

        // Контроль наявності серцебиття
        if (state_ == FtsState::Armed) {
            if ((now - lastHeartbeat_) > HeartbeatTimeout) {
                state_ = FtsState::LinkLost;
                triggerTermination();
                return;
            }
        }

        // Послідовна активація піропатрона парашута
        if (state_ == FtsState::TerminationTriggered && parachuteArmed_ && !parachuteFired_) {
            if ((now - terminationTimestamp_) >= ParachuteDelay) {
                hal_.setParachutePyro(true);
                parachuteFired_ = true;
                state_ = FtsState::ParachuteDeployed;
            }
        }
    }

    [[nodiscard]] FtsState state() const noexcept { return state_; }
    [[nodiscard]] bool isArmed() const noexcept { return state_ == FtsState::Armed; }

private:
    static constexpr uint16_t calculateCrc16(std::span<const uint8_t> data) noexcept {
        uint16_t crc = 0xFFFFU;
        for (const uint8_t byte : data) {
            crc ^= static_cast<uint16_t>(static_cast<uint16_t>(byte) << 8);
            for (uint8_t bit = 0; bit < 8; ++bit) {
                if (crc & 0x8000U) {
                    crc = static_cast<uint16_t>((crc << 1) ^ 0x1021U);
                } else {
                    crc = static_cast<uint16_t>(crc << 1);
                }
            }
        }
        return crc;
    }

    Hal& hal_;
    PlatformType platform_;
    FtsState state_{FtsState::Disarmed};
    Milliseconds lastHeartbeat_{0};
    Milliseconds terminationTimestamp_{0};
    bool parachuteArmed_{false};
    bool parachuteFired_{false};
};
