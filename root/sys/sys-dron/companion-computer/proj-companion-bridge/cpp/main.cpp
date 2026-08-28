// ============================================================================
// Високопродуктивний міст MAVLink між MCU та Companion (C++20)
// ============================================================================
#include <iostream>
#include <vector>
#include <span>
#include <chrono>
#include <optional>
#include <expected>
#include <string>
#include <string_view>
#include <memory>
#include <cstdint>
#include <cstring>
#include <unistd.h>
#include <fcntl.h>
#include <termios.h>
#include <sys/epoll.h>

namespace drone::bridge {

struct MavlinkHeader {
    uint8_t length{0};
    uint8_t incompat_flags{0};
    uint8_t compat_flags{0};
    uint8_t seq{0};
    uint8_t sys_id{0};
    uint8_t comp_id{0};
    uint32_t msg_id{0};
};

struct MavlinkMessage {
    MavlinkHeader header;
    std::vector<uint8_t> payload;
    uint16_t checksum{0};
};

struct LocalNedSetpoint {
    float x{0.0f};
    float y{0.0f};
    float z{0.0f};
    float yaw{0.0f};
};

enum class BridgeError {
    DeviceNotFound,
    ConfigurationFailed,
    WriteError,
    BufferOverflow,
    Timeout,
    ReadError
};

class CompanionBridge {
public:
    static constexpr uint8_t STX_V2 = 0xFD;
    static constexpr std::size_t RX_BUFFER_SIZE = 8192;

    explicit CompanionBridge(std::string_view port_name, speed_t baud = B921600)
        : port_name_(port_name), baudrate_(baud), rx_ring_(RX_BUFFER_SIZE) {}

    ~CompanionBridge() noexcept {
        stop();
    }

    CompanionBridge(const CompanionBridge&) = delete;
    CompanionBridge& operator=(const CompanionBridge&) = delete;
    CompanionBridge(CompanionBridge&&) noexcept = default;
    CompanionBridge& operator=(CompanionBridge&&) noexcept = default;

    [[nodiscard]] std::expected<void, BridgeError> start() {
        fd_ = ::open(port_name_.c_str(), O_RDWR | O_NOCTTY | O_NONBLOCK);
        if (fd_ < 0) {
            return std::unexpected(BridgeError::DeviceNotFound);
        }

        struct termios tty{};
        if (::tcgetattr(fd_, &tty) != 0) {
            stop();
            return std::unexpected(BridgeError::ConfigurationFailed);
        }

        ::cfmakeraw(&tty);
        ::cfsetispeed(&tty, baudrate_);
        ::cfsetospeed(&tty, baudrate_);

        tty.c_cflag |= (CLOCAL | CREAD | CS8);
        tty.c_cflag &= ~(PARENB | CSTOPB | CRTSCTS);
        tty.c_cc[VMIN] = 0;
        tty.c_cc[VTIME] = 0;

        if (::tcsetattr(fd_, TCSANOW, &tty) != 0) {
            stop();
            return std::unexpected(BridgeError::ConfigurationFailed);
        }

        epoll_fd_ = ::epoll_create1(0);
        if (epoll_fd_ < 0) {
            stop();
            return std::unexpected(BridgeError::ConfigurationFailed);
        }

        struct epoll_event ev{};
        ev.events = EPOLLIN | EPOLLET;
        ev.data.fd = fd_;
        if (::epoll_ctl(epoll_fd_, EPOLL_CTL_ADD, fd_, &ev) < 0) {
            stop();
            return std::unexpected(BridgeError::ConfigurationFailed);
        }

        last_heartbeat_ = std::chrono::steady_clock::now();
        return {};
    }

    void stop() noexcept {
        if (epoll_fd_ >= 0) {
            ::close(epoll_fd_);
            epoll_fd_ = -1;
        }
        if (fd_ >= 0) {
            ::close(fd_);
            fd_ = -1;
        }
    }

    // Очікування нових байтів через epoll та вичитування у кільцевий буфер
    std::expected<std::size_t, BridgeError> poll_and_read(int timeout_ms = 10) {
        if (epoll_fd_ < 0 || fd_ < 0) return std::unexpected(BridgeError::DeviceNotFound);

        struct epoll_event events[4];
        int nfds = ::epoll_wait(epoll_fd_, events, 4, timeout_ms);
        if (nfds < 0) {
            if (errno == EINTR) return 0;
            return std::unexpected(BridgeError::ReadError);
        }

        std::size_t total_bytes = 0;
        uint8_t buffer[512];
        for (int i = 0; i < nfds; ++i) {
            if (events[i].data.fd == fd_) {
                while (true) {
                    auto n = ::read(fd_, buffer, sizeof(buffer));
                    if (n > 0) {
                        for (ssize_t j = 0; j < n; ++j) {
                            push_byte(buffer[j]);
                        }
                        total_bytes += n;
                    } else {
                        break;
                    }
                }
            }
        }
        return total_bytes;
    }

    // Відправка уставки положення
    [[nodiscard]] std::expected<void, BridgeError> send_setpoint(const LocalNedSetpoint& sp) {
        std::vector<uint8_t> frame(65);
        frame[0] = STX_V2;
        frame[1] = 53; // payload len
        frame[2] = 0;
        frame[3] = 0;
        frame[4] = seq_++;
        frame[5] = 1;   // SysID
        frame[6] = 191; // CompID Companion
        frame[7] = 84;  // MSG_ID SET_POSITION_TARGET_LOCAL_NED
        frame[8] = 0;
        frame[9] = 0;

        auto now_ms = static_cast<uint32_t>(
            std::chrono::duration_cast<std::chrono::milliseconds>(
                std::chrono::steady_clock::now().time_since_epoch()
            ).count()
        );

        std::memcpy(&frame[10], &now_ms, 4);
        frame[14] = 1; // Target Sys
        frame[15] = 1; // Target Comp
        frame[16] = 1; // MAV_FRAME_LOCAL_NED
        uint16_t type_mask = 0b0000101111111000;
        std::memcpy(&frame[17], &type_mask, 2);
        std::memcpy(&frame[19], &sp.x, 4);
        std::memcpy(&frame[23], &sp.y, 4);
        std::memcpy(&frame[27], &sp.z, 4);

        uint16_t crc = 0x55AA;
        std::memcpy(&frame[63], &crc, 2);

        auto written = ::write(fd_, frame.data(), frame.size());
        if (written != static_cast<ssize_t>(frame.size())) {
            return std::unexpected(BridgeError::WriteError);
        }
        return {};
    }

    [[nodiscard]] bool is_healthy(std::chrono::milliseconds timeout = std::chrono::milliseconds(1000)) const noexcept {
        return (std::chrono::steady_clock::now() - last_heartbeat_) < timeout;
    }

private:
    void push_byte(uint8_t byte) noexcept {
        if (byte == STX_V2) {
            last_heartbeat_ = std::chrono::steady_clock::now();
        }
        rx_ring_[head_] = byte;
        head_ = (head_ + 1) % rx_ring_.size();
    }

    int fd_{-1};
    int epoll_fd_{-1};
    std::string port_name_;
    speed_t baudrate_;
    uint8_t seq_{0};
    std::vector<uint8_t> rx_ring_;
    std::size_t head_{0};
    std::size_t tail_{0};
    std::chrono::steady_clock::time_point last_heartbeat_{};
};

} // namespace drone::bridge
