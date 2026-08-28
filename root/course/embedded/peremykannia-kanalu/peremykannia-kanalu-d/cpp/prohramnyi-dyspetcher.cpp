#include <cstdint>
#include <cstddef>
#include <span>
#include <array>
#include <chrono>
#include <string_view>

namespace embedded::net {

using namespace std::chrono_literals;

enum class InterfaceState : uint8_t {
    Disabled,
    Standby,
    Connecting,
    Online,
    Degraded,
    Failed
};

struct [[nodiscard]] ITransportChannel {
    virtual ~ITransportChannel() = default;
    [[nodiscard]] virtual std::string_view name() const noexcept = 0;
    [[nodiscard]] virtual bool isPrimary() const noexcept = 0;
    [[nodiscard]] virtual bool setPower(bool enable) noexcept = 0;
    [[nodiscard]] virtual bool connect() noexcept = 0;
    virtual void disconnect() noexcept = 0;
    [[nodiscard]] virtual bool checkPhyLink() noexcept = 0;
    [[nodiscard]] virtual bool sendPacket(std::span<const uint8_t> data) noexcept = 0;
    [[nodiscard]] virtual bool sendHealthProbe() noexcept = 0;
};

class FailoverManager {
public:
    struct Config {
        std::chrono::milliseconds probeInterval{5000ms};
        std::chrono::milliseconds holdDownTime{60000ms};
        std::chrono::milliseconds fallbackDelay{180000ms};
        uint8_t failureThreshold{3};
    };

    constexpr explicit FailoverManager(ITransportChannel& primary, 
                                       ITransportChannel& backup, 
                                       Config cfg = {}) noexcept
        : primary_{primary}, backup_{backup}, config_{cfg} {}

    void init(std::chrono::milliseconds now) noexcept {
        primary_.setPower(true);
        if (primary_.connect()) {
            primaryState_ = InterfaceState::Connecting;
        }
        backupState_ = InterfaceState::Standby;
        activeChannel_ = &primary_;
        lastSwitchTime_ = now;
    }

    void poll(std::chrono::milliseconds now) noexcept {
        // 1. Апаратний моніторинг PHY
        if (!primary_.checkPhyLink()) {
            primaryFailures_ = config_.failureThreshold;
            primaryState_ = InterfaceState::Failed;
        }

        // 2. Періодичний зонд основного каналу
        if (now - lastPrimaryProbe_ >= config_.probeInterval) {
            lastPrimaryProbe_ = now;
            if (primary_.checkPhyLink() && primary_.sendHealthProbe()) {
                primaryFailures_ = 0;
                if (++primarySuccesses_ >= 2) {
                    primaryState_ = InterfaceState::Online;
                }
            } else {
                primarySuccesses_ = 0;
                if (++primaryFailures_ >= config_.failureThreshold) {
                    primaryState_ = InterfaceState::Failed;
                }
            }
        }

        // 3. Автоматичний перехід на резерв (Failover)
        if (activeChannel_ == &primary_ && primaryState_ == InterfaceState::Failed) {
            backup_.setPower(true);
            if (backup_.connect()) {
                backupState_ = InterfaceState::Online;
                activeChannel_ = &backup_;
                lastSwitchTime_ = now;
                fallbackStarted_ = false;
            }
        }

        // 4. Повернення на основний канал з урахуванням захисту від брязкоту
        if (activeChannel_ == &backup_) {
            const bool holdExpired = (now - lastSwitchTime_) >= config_.holdDownTime;

            if (primaryState_ == InterfaceState::Online && holdExpired) {
                if (!fallbackStarted_) {
                    fallbackStarted_ = true;
                    fallbackStartTime_ = now;
                } else if ((now - fallbackStartTime_) >= config_.fallbackDelay) {
                    // Карантинний період успішно пройдено
                    activeChannel_ = &primary_;
                    fallbackStarted_ = false;
                    lastSwitchTime_ = now;

                    backup_.disconnect();
                    backup_.setPower(false);
                    backupState_ = InterfaceState::Standby;
                }
            } else {
                fallbackStarted_ = false;
            }
        }
    }

    [[nodiscard]] bool transmit(std::span<const uint8_t> payload) noexcept {
        if (activeChannel_ == &primary_ && primaryState_ != InterfaceState::Online) {
            return false;
        }
        if (activeChannel_ == &backup_ && backupState_ != InterfaceState::Online) {
            return false;
        }
        return activeChannel_->sendPacket(payload);
    }

    [[nodiscard]] std::string_view activeInterfaceName() const noexcept {
        return activeChannel_->name();
    }

private:
    ITransportChannel& primary_;
    ITransportChannel& backup_;
    Config config_;

    ITransportChannel* activeChannel_{nullptr};
    InterfaceState primaryState_{InterfaceState::Disabled};
    InterfaceState backupState_{InterfaceState::Disabled};

    std::chrono::milliseconds lastPrimaryProbe_{0ms};
    std::chrono::milliseconds lastSwitchTime_{0ms};
    std::chrono::milliseconds fallbackStartTime_{0ms};

    uint8_t primaryFailures_{0};
    uint8_t primarySuccesses_{0};
    bool fallbackStarted_{false};
};

} // namespace embedded::net
