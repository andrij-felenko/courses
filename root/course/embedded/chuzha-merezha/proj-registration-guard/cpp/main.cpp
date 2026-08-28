#include <cstdint>
#include <chrono>
#include <string_view>
#include <optional>
#include <algorithm>

using namespace std::chrono_literals;

enum class GuardState {
    PowerOff,
    Boot,
    CheckRegistration,
    OnlineTransmission,
    Recovery,
    BackoffSleep
};

enum class RegistrationStatus {
    NotSearching = 0,
    HomeNetwork = 1,
    Searching = 2,
    RegistrationDenied = 3,
    Unknown = 4,
    Roaming = 5
};

class IModemHardware {
public:
    virtual ~IModemHardware() = default;
    virtual void setPower(bool enable) = 0;
    virtual bool sendCommand(std::string_view cmd, std::string_view expected, std::chrono::milliseconds timeout) = 0;
    virtual RegistrationStatus queryRegistration() = 0;
};

class CellularRegistrationGuard {
public:
    explicit CellularRegistrationGuard(IModemHardware& hw)
        : hardware_(hw) {}

    void process(std::chrono::milliseconds now) {
        const auto elapsed = now - stateEnterTime_;

        switch (state_) {
        case GuardState::PowerOff:
            hardware_.setPower(true);
            transitionTo(GuardState::Boot, now);
            break;

        case GuardState::Boot:
            if (hardware_.sendCommand("AT\r", "OK", 1000ms)) {
                hardware_.sendCommand("AT+CEREG=2\r", "OK", 1000ms);
                transitionTo(GuardState::CheckRegistration, now);
            } else if (elapsed > 10000ms) {
                transitionTo(GuardState::Recovery, now);
            }
            break;

        case GuardState::CheckRegistration: {
            const auto status = hardware_.queryRegistration();
            if (status == RegistrationStatus::HomeNetwork || status == RegistrationStatus::Roaming) {
                failedAttempts_ = 0;
                backoffInterval_ = baseBackoff_;
                transitionTo(GuardState::OnlineTransmission, now);
            } else if (status == RegistrationStatus::RegistrationDenied || elapsed > maxRegistrationTimeout_) {
                ++failedAttempts_;
                transitionTo(GuardState::Recovery, now);
            }
            break;
        }

        case GuardState::Recovery:
            // Очищення чорних списків модема та примусовий автоматичний вибір мережі
            hardware_.sendCommand("AT+CFUN=0\r", "OK", 3000ms);
            hardware_.sendCommand("AT+CFUN=1\r", "OK", 3000ms);
            hardware_.sendCommand("AT+COPS=0\r", "OK", 5000ms);

            hardware_.setPower(false);
            transitionTo(GuardState::BackoffSleep, now);
            break;

        case GuardState::BackoffSleep:
            if (elapsed >= backoffInterval_) {
                backoffInterval_ = std::min(backoffInterval_ * 2, maxBackoff_);
                transitionTo(GuardState::PowerOff, now);
            }
            break;

        case GuardState::OnlineTransmission:
            break;
        }
    }

    [[nodiscard]] GuardState currentState() const noexcept { return state_; }
    [[nodiscard]] std::chrono::seconds currentBackoff() const noexcept { return backoffInterval_; }

private:
    void transitionTo(GuardState newState, std::chrono::milliseconds now) noexcept {
        state_ = newState;
        stateEnterTime_ = now;
    }

    IModemHardware& hardware_;
    GuardState state_{GuardState::PowerOff};
    std::chrono::milliseconds stateEnterTime_{0ms};

    static constexpr auto baseBackoff_ = 60s;
    static constexpr auto maxBackoff_ = 14400s; // 4 години
    static constexpr auto maxRegistrationTimeout_ = 45000ms;

    std::chrono::seconds backoffInterval_{baseBackoff_};
    std::uint32_t failedAttempts_{0};
};
