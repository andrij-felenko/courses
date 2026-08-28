#include <cstdint>
#include <string_view>
#include <chrono>
#include <expected>
#include <array>
#include <span>

enum class ModemRat : uint8_t {
    Gsm2G = 12,
    Lte4G = 28,
    Nr5G  = 30,
    Auto  = 255
};

enum class FsmState : uint8_t {
    PowerOff,
    PulsePwrkey,
    WaitBoot,
    SyncAt,
    ConfigRat,
    WaitNetwork,
    TransmitData,
    EnterPsm,
    ErrorRecovery
};

enum class DriverError {
    Timeout,
    SimLocked,
    RegistrationDenied,
    HardwareFault
};

class CellularModem {
public:
    explicit CellularModem(ModemRat rat) noexcept
        : target_rat_(rat), state_(FsmState::PowerOff), backoff_(std::chrono::seconds(1)) {}

    void step(std::string_view rx_line, std::chrono::milliseconds now) noexcept {
        switch (state_) {
            case FsmState::PowerOff:
                set_pwrkey(true);
                state_timer_ = now;
                state_ = FsmState::PulsePwrkey;
                break;

            case FsmState::PulsePwrkey:
                if (now - state_timer_ >= std::chrono::milliseconds(800)) {
                    set_pwrkey(false);
                    state_timer_ = now;
                    state_ = FsmState::WaitBoot;
                }
                break;

            case FsmState::WaitBoot:
                if (now - state_timer_ >= std::chrono::milliseconds(2500)) {
                    retries_ = 0;
                    send_command("ATE0\r\n");
                    state_timer_ = now;
                    state_ = FsmState::SyncAt;
                }
                break;

            case FsmState::SyncAt:
                if (rx_line.find("OK") != std::string_view::npos) {
                    if (target_rat_ == ModemRat::Lte4G) {
                        send_command("AT+WS46=28\r\n");
                    } else if (target_rat_ == ModemRat::Gsm2G) {
                        send_command("AT+WS46=12\r\n");
                    } else {
                        send_command("AT+WS46=255\r\n");
                    }
                    state_timer_ = now;
                    state_ = FsmState::ConfigRat;
                } else if (now - state_timer_ >= std::chrono::seconds(1)) {
                    if (++retries_ > 10) {
                        state_ = FsmState::ErrorRecovery;
                    } else {
                        send_command("AT\r\n");
                        state_timer_ = now;
                    }
                }
                break;

            case FsmState::ConfigRat:
                if (rx_line.find("OK") != std::string_view::npos) {
                    send_command("AT+CEREG=2;+CESQ\r\n");
                    state_timer_ = now;
                    state_ = FsmState::WaitNetwork;
                } else if (now - state_timer_ >= std::chrono::seconds(3)) {
                    state_ = FsmState::ErrorRecovery;
                }
                break;

            case FsmState::WaitNetwork:
                if (rx_line.find("+CEREG: 2,1") != std::string_view::npos ||
                    rx_line.find("+CEREG: 2,5") != std::string_view::npos) {
                    registered_ = true;
                    state_ = FsmState::TransmitData;
                } else if (now - state_timer_ >= std::chrono::seconds(60)) {
                    state_ = FsmState::ErrorRecovery;
                }
                break;

            case FsmState::TransmitData:
                send_command("AT+QMTOPEN=...\r\n");
                state_ = FsmState::EnterPsm;
                break;

            case FsmState::EnterPsm:
                send_command("AT+CPSMS=1,,,\"00111000\",\"00000010\"\r\n");
                set_dtr(true);
                break;

            case FsmState::ErrorRecovery:
                backoff_ = std::min(backoff_ * 2, std::chrono::seconds(900));
                set_dtr(true);
                state_ = FsmState::PowerOff;
                break;
        }
    }

    [[nodiscard]] bool is_registered() const noexcept { return registered_; }
    [[nodiscard]] FsmState current_state() const noexcept { return state_; }

private:
    void send_command(std::string_view cmd) noexcept {
        /* Платформне надсилання байтів у UART */
    }

    void set_pwrkey(bool active) noexcept {
        /* Керування лінією PWRKEY через GPIO */
    }

    void set_dtr(bool active) noexcept {
        /* Керування лінією сну DTR */
    }

    ModemRat target_rat_;
    FsmState state_;
    std::chrono::milliseconds state_timer_{0};
    std::chrono::seconds backoff_;
    uint8_t retries_{0};
    bool registered_{false};
};
