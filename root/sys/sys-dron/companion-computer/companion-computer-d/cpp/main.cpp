// ============================================================================
// Драйвер послідовного порту MAVLink для бортового комп'ютера (C++20)
// ============================================================================
#include <iostream>
#include <vector>
#include <span>
#include <chrono>
#include <optional>
#include <string>
#include <string_view>
#include <system_error>
#include <cstdint>
#include <cstring>
#include <unistd.h>
#include <fcntl.h>
#include <termios.h>

class MavlinkSerialBridge {
public:
    static constexpr uint8_t STX_V2 = 0xFD;

    explicit MavlinkSerialBridge(std::string_view port, speed_t baud = B921600)
        : port_name_(port), baudrate_(baud) {}

    ~MavlinkSerialBridge() noexcept {
        close_port();
    }

    // Заборона копіювання для захисту дескриптора (RAII)
    MavlinkSerialBridge(const MavlinkSerialBridge&) = delete;
    MavlinkSerialBridge& operator=(const MavlinkSerialBridge&) = delete;

    MavlinkSerialBridge(MavlinkSerialBridge&& other) noexcept
        : fd_(other.fd_), port_name_(std::move(other.port_name_)),
          baudrate_(other.baudrate_), last_heartbeat_(other.last_heartbeat_) {
        other.fd_ = -1;
    }

    bool open_port() {
        fd_ = ::open(port_name_.c_str(), O_RDWR | O_NOCTTY | O_NONBLOCK);
        if (fd_ < 0) {
            return false;
        }

        struct termios tty{};
        if (::tcgetattr(fd_, &tty) != 0) {
            close_port();
            return false;
        }

        ::cfmakeraw(&tty);
        ::cfsetispeed(&tty, baudrate_);
        ::cfsetospeed(&tty, baudrate_);

        tty.c_cflag |= (CLOCAL | CREAD | CS8);
        tty.c_cflag &= ~(PARENB | CSTOPB | CRTSCTS);
        tty.c_cc[VMIN] = 0;
        tty.c_cc[VTIME] = 0;

        if (::tcsetattr(fd_, TCSANOW, &tty) != 0) {
            close_port();
            return false;
        }

        ::tcflush(fd_, TCIOFLUSH);
        last_heartbeat_ = std::chrono::steady_clock::now();
        return true;
    }

    void close_port() noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
            fd_ = -1;
        }
    }

    // Відправка буфера без зайвого копіювання через std::span
    [[nodiscard]] bool send_packet(std::span<const uint8_t> packet) const noexcept {
        if (fd_ < 0 || packet.empty()) return false;
        auto written = ::write(fd_, packet.data(), packet.size());
        return written == static_cast<ssize_t>(packet.size());
    }

    // Неблокуюче читання вхідних байтів
    std::size_t receive_bytes(std::span<uint8_t> out_buffer) {
        if (fd_ < 0 || out_buffer.empty()) return 0;
        auto bytes_read = ::read(fd_, out_buffer.data(), out_buffer.size());
        if (bytes_read > 0) {
            for (ssize_t i = 0; i < bytes_read; ++i) {
                if (out_buffer[i] == STX_V2) {
                    last_heartbeat_ = std::chrono::steady_clock::now();
                }
            }
            return static_cast<std::size_t>(bytes_read);
        }
        return 0;
    }

    // Перевірка активності каналу зв'язку
    [[nodiscard]] bool is_connected(std::chrono::milliseconds timeout = std::chrono::milliseconds(1000)) const noexcept {
        auto now = std::chrono::steady_clock::now();
        return (now - last_heartbeat_) < timeout;
    }

private:
    int fd_{-1};
    std::string port_name_;
    speed_t baudrate_;
    std::chrono::steady_clock::time_point last_heartbeat_{};
};
