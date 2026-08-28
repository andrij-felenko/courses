/* service_engine.cpp — Сучасний C++20 сервісний діагностичний контролер */
#include <cstdint>
#include <string_view>
#include <array>
#include <chrono>
#include <format>
#include <expected>
#include <span>

class ServiceEngine {
public:
    enum class State : uint8_t {
        Locked,
        ChallengeIssued,
        Unlocked,
        EmergencyStop
    };

    enum class ErrorCode : uint16_t {
        Locked               = 0x4000,
        AccessDenied         = 0x4001,
        InvalidChannel       = 0x4002,
        TimeoutOutOfRange    = 0x4003,
        AuthFailed           = 0x4004,
        BadArguments         = 0x4005,
        UnknownCommand       = 0x4006
    };

    ServiceEngine() = default;

    void feedByte(char c) noexcept {
        if (c == '\r' || c == '\n') {
            if (rxIdx_ > 0) {
                std::string_view line(rxBuf_.data(), rxIdx_);
                dispatch(line);
                rxIdx_ = 0;
                if (state_ == State::Unlocked) {
                    sendString("SRV> ");
                }
            }
        } else if (rxIdx_ < rxBuf_.size() - 1 && c >= 0x20 && c <= 0x7E) {
            rxBuf_[rxIdx_++] = c;
        }
    }

    void poll(std::chrono::milliseconds now) noexcept {
        if (activeChannel_ != 0 && now >= actTimerDeadline_) {
            emergencyAllOff();
            sendString("\r\n[EVENT: ACTUATION_TIMEOUT_AUTO_SHUTDOWN]\r\nSRV> ");
        }

        if (state_ == State::Unlocked && now >= sessionDeadline_) {
            emergencyAllOff();
            state_ = State::Locked;
            sendString("\r\n[EVENT: SESSION_TIMEOUT_LOCKED]\r\n");
        }
    }

    void emergencyAllOff() noexcept {
        hwSetRelay(1, false);
        hwSetRelay(2, false);
        activeChannel_ = 0;
    }

private:
    static constexpr size_t BufferSize = 128;
    static constexpr auto SessionTimeout = std::chrono::minutes(15);
    static constexpr auto MaxActTimeout = std::chrono::seconds(15);

    State state_{State::Locked};
    uint8_t activeChannel_{0};
    std::chrono::milliseconds sessionDeadline_{0};
    std::chrono::milliseconds actTimerDeadline_{0};
    uint32_t currentNonce_{0};

    std::array<char, BufferSize> rxBuf_{};
    size_t rxIdx_{0};

    void dispatch(std::string_view cmd) noexcept {
        if (cmd == "auth challenge") {
            currentNonce_ = hwGetRandom();
            state_ = State::ChallengeIssued;
            sendString(std::format("+OK: CHALLENGE 0x{:08X}\r\n", currentNonce_));
            return;
        }

        if (cmd.starts_with("auth key ")) {
            auto key = cmd.substr(9);
            if (key == "SRV_PASS_2026") {
                state_ = State::Unlocked;
                sessionDeadline_ = hwNow() + SessionTimeout;
                sendString("+OK: SERVICE_UNLOCKED (SESSION 15 MIN)\r\n");
            } else {
                state_ = State::Locked;
                sendError(ErrorCode::AuthFailed, "AUTH_FAILED");
            }
            return;
        }

        if (state_ != State::Unlocked) {
            sendError(ErrorCode::Locked, "LOCKED_ENTER_AUTH_FIRST");
            return;
        }

        sessionDeadline_ = hwNow() + SessionTimeout;

        if (cmd == "diag selftest") {
            executeSelftest();
        } else if (cmd == "sys lock") {
            emergencyAllOff();
            state_ = State::Locked;
            sendString("+OK: SERVICE_LOCKED\r\n");
        } else {
            sendError(ErrorCode::UnknownCommand, "UNKNOWN_COMMAND");
        }
    }

    void executeSelftest() noexcept {
        bool rtcOk = hwI2cProbe(0x68);
        bool eepromOk = hwI2cProbe(0x50);
        uint16_t adc0 = hwAdcRead(0);
        sendString(std::format("+OK: BIST (RTC:{}, EEPROM:{}, ADC0_RAW:0x{:04X})\r\n",
                               rtcOk ? "OK" : "FAULT",
                               eepromOk ? "OK" : "FAULT",
                               adc0));
    }

    void sendString(std::string_view str) noexcept {
        hwUartWrite(str);
    }

    void sendError(ErrorCode code, std::string_view msg) noexcept {
        sendString(std::format("-ERR: 0x{:04X} {}\r\n", static_cast<uint16_t>(code), msg));
    }

    /* Апаратні проксі-методи */
    static std::chrono::milliseconds hwNow() noexcept;
    static uint32_t hwGetRandom() noexcept;
    static void hwUartWrite(std::string_view s) noexcept;
    static void hwSetRelay(uint8_t ch, bool state) noexcept;
    static bool hwI2cProbe(uint8_t addr) noexcept;
    static uint16_t hwAdcRead(uint8_t ch) noexcept;
};
