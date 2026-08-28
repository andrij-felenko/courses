#pragma once

#include <cstdint>
#include <vector>
#include <string>
#include <string_view>
#include <span>
#include <array>
#include <chrono>
#include <optional>
#include <expected>
#include <termios.h>
#include <fcntl.h>
#include <unistd.h>
#include <algorithm>

namespace satellite {

enum class BridgeErrorCode {
    DeviceNotFound,
    PortConfigurationFailed,
    WriteTimeout,
    ChecksumMismatch,
    SignalUnavailable,
    RateLimitTriggered,
    PayloadTooLarge
};

enum class FsmState {
    Idle,
    QuerySignalQuality,
    LoadBinaryBuffer,
    TransmitSbdSession,
    ReceiveIncomingPayload,
    FlushBuffers,
    ErrorBackoff
};

struct SbdSessionStatus {
    int mo_status{0};
    int momsn{0};
    int mt_status{0};
    int mtmsn{0};
    int mt_length{0};
    int mt_queued{0};
};

class AsyncIridiumBridge {
public:
    explicit AsyncIridiumBridge(std::string serial_port_path, 
                                std::chrono::seconds rate_limit = std::chrono::seconds(20))
        : port_path_(std::move(serial_port_path)),
          min_interval_(rate_limit),
          last_update_(std::chrono::steady_clock::now()) {}

    ~AsyncIridiumBridge() noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    AsyncIridiumBridge(const AsyncIridiumBridge&) = delete;
    AsyncIridiumBridge& operator=(const AsyncIridiumBridge&) = delete;
    AsyncIridiumBridge(AsyncIridiumBridge&&) noexcept = default;
    AsyncIridiumBridge& operator=(AsyncIridiumBridge&&) noexcept = default;

    std::expected<void, BridgeErrorCode> initializePort() noexcept {
        fd_ = ::open(port_path_.c_str(), O_RDWR | O_NOCTTY | O_NDELAY);
        if (fd_ < 0) {
            return std::unexpected(BridgeErrorCode::DeviceNotFound);
        }

        struct termios tty{};
        if (::tcgetattr(fd_, &tty) != 0) {
            ::close(fd_);
            fd_ = -1;
            return std::unexpected(BridgeErrorCode::PortConfigurationFailed);
        }

        ::cfsetispeed(&tty, B19200);
        ::cfsetospeed(&tty, B19200);

        tty.c_cflag |= (CLOCAL | CREAD | CS8 | CRTSCTS);
        tty.c_cflag &= ~(PARENB | CSTOPB | CSIZE);
        tty.c_iflag &= ~(IGNBRK | BRKINT | PARMRK | ISTRIP | INLCR | IGNCR | ICRNL | IXON | IXOFF);
        tty.c_oflag &= ~OPOST;
        tty.c_lflag &= ~(ECHO | ECHONL | ICANON | ISIG | IEXTEN);

        if (::tcsetattr(fd_, TCSANOW, &tty) != 0) {
            ::close(fd_);
            fd_ = -1;
            return std::unexpected(BridgeErrorCode::PortConfigurationFailed);
        }
        return {};
    }

    std::expected<void, BridgeErrorCode> pushTelemetryFrame(std::span<const uint8_t> frame) noexcept {
        if (frame.size() > 340) {
            return std::unexpected(BridgeErrorCode::PayloadTooLarge);
        }
        
        // Оновлення буфера MO свіжими даними
        tx_payload_.assign(frame.begin(), frame.end());
        return {};
    }

    void tick() noexcept {
        replenishTokens();

        switch (current_state_) {
            case FsmState::Idle:
                if (!tx_payload_.empty() && token_count_ >= 1.0f) {
                    current_state_ = FsmState::QuerySignalQuality;
                    transmitCommand("AT+CSQ\r");
                }
                break;

            case FsmState::QuerySignalQuality:
                current_state_ = FsmState::LoadBinaryBuffer;
                writeBinaryPayload();
                break;

            case FsmState::LoadBinaryBuffer:
                current_state_ = FsmState::TransmitSbdSession;
                transmitCommand("AT+SBDIX\r");
                break;

            case FsmState::TransmitSbdSession:
                token_count_ -= 1.0f;
                tx_payload_.clear();
                current_state_ = FsmState::FlushBuffers;
                transmitCommand("AT+SBDD0\r");
                break;

            case FsmState::FlushBuffers:
                current_state_ = FsmState::Idle;
                break;

            default:
                current_state_ = FsmState::Idle;
                break;
        }
    }

    [[nodiscard]] FsmState state() const noexcept { return current_state_; }
    [[nodiscard]] float availableTokens() const noexcept { return token_count_; }

private:
    void replenishTokens() noexcept {
        const auto now = std::chrono::steady_clock::now();
        const std::chrono::duration<float> elapsed = now - last_update_;
        last_update_ = now;

        const float interval_sec = static_cast<float>(min_interval_.count());
        token_count_ = std::min(2.0f, token_count_ + elapsed.count() / interval_sec);
    }

    void transmitCommand(std::string_view cmd) noexcept {
        if (fd_ >= 0) {
            [[maybe_unused]] auto res = ::write(fd_, cmd.data(), cmd.size());
        }
    }

    void writeBinaryPayload() noexcept {
        if (fd_ < 0 || tx_payload_.empty()) return;

        std::string cmd = "AT+SBDWB=" + std::to_string(tx_payload_.size()) + "\r";
        transmitCommand(cmd);
        ::usleep(100000);

        uint16_t checksum = 0;
        for (uint8_t byte : tx_payload_) checksum += byte;

        std::array<uint8_t, 2> cs = {
            static_cast<uint8_t>(checksum >> 8),
            static_cast<uint8_t>(checksum & 0xFF)
        };

        [[maybe_unused]] auto w1 = ::write(fd_, tx_payload_.data(), tx_payload_.size());
        [[maybe_unused]] auto w2 = ::write(fd_, cs.data(), cs.size());
    }

    std::string port_path_;
    int fd_{-1};
    FsmState current_state_{FsmState::Idle};
    std::chrono::seconds min_interval_;
    std::chrono::steady_clock::time_point last_update_{};
    float token_count_{1.0f};
    std::vector<uint8_t> tx_payload_;
};

} // namespace satellite
