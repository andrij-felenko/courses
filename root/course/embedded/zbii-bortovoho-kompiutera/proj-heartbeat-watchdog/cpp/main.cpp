#include <iostream>
#include <string_view>
#include <span>
#include <chrono>
#include <thread>
#include <vector>
#include <expected>
#include <system_error>
#include <cstdint>
#include <cstring>
#include <fcntl.h>
#include <unistd.h>
#include <termios.h>
#include <sched.h>
#include <sys/mman.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <sys/stat.h>
#include <gpiod.h>

namespace companion {

using namespace std::chrono_literals;

inline constexpr std::string_view kSocketPath{"/tmp/companion_health.sock"};
inline constexpr std::string_view kSerialPort{"/dev/ttyAMA0"};
inline constexpr std::string_view kGpioChip{"gpiochip0"};
inline constexpr unsigned int kWatchdogPin = 17;

inline constexpr auto kHeartbeatPeriod = 1000ms;
inline constexpr auto kStrobePeriod = 100ms;
inline constexpr auto kProcessTimeout = 2s;

#pragma pack(push, 1)
struct MavlinkHeartbeatPayload {
    std::uint32_t custom_mode{0};
    std::uint8_t  type{18};            // MAV_TYPE_ONBOARD_CONTROLLER
    std::uint8_t  autopilot{8};         // MAV_AUTOPILOT_INVALID
    std::uint8_t  base_mode{1};         // MAV_MODE_FLAG_CUSTOM_MODE_ENABLED
    std::uint8_t  system_status{3};     // 3=ACTIVE, 5=CRITICAL
    std::uint8_t  mavlink_version{3};
};

struct MavlinkV2HeartbeatPacket {
    std::uint8_t  magic{0xFD};
    std::uint8_t  len{sizeof(MavlinkHeartbeatPayload)};
    std::uint8_t  incompat_flags{0};
    std::uint8_t  compat_flags{0};
    std::uint8_t  seq{0};
    std::uint8_t  sysid{1};
    std::uint8_t  compid{191};          // MAV_COMP_ID_ONBOARD_COMPUTER
    std::uint8_t  msgid[3]{0, 0, 0};
    MavlinkHeartbeatPayload payload{};
    std::uint16_t checksum{0};
};
#pragma pack(pop)

class FileDescriptor {
public:
    explicit FileDescriptor(int fd = -1) noexcept : fd_{fd} {}
    ~FileDescriptor() { reset(); }

    FileDescriptor(const FileDescriptor&) = delete;
    FileDescriptor& operator=(const FileDescriptor&) = delete;

    FileDescriptor(FileDescriptor&& other) noexcept : fd_{other.release()} {}
    FileDescriptor& operator=(FileDescriptor&& other) noexcept {
        if (this != &other) {
            reset(other.release());
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }

    int release() noexcept {
        int old = fd_;
        fd_ = -1;
        return old;
    }

    void reset(int new_fd = -1) noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
        }
        fd_ = new_fd;
    }

private:
    int fd_{-1};
};

class GpioLineGuard {
public:
    GpioLineGuard(std::string_view chip_name, unsigned int pin) {
        chip_ = gpiod_chip_open_by_name(chip_name.data());
        if (chip_) {
            line_ = gpiod_chip_get_line(chip_, pin);
            if (line_) {
                gpiod_line_request_output(line_, "companion-watchdog-cpp", 0);
            }
        }
    }

    ~GpioLineGuard() {
        if (line_) {
            gpiod_line_release(line_);
        }
        if (chip_) {
            gpiod_chip_close(chip_);
        }
    }

    void set_level(int value) noexcept {
        if (line_) {
            gpiod_line_set_value(line_, value);
        }
    }

    [[nodiscard]] bool available() const noexcept { return line_ != nullptr; }

private:
    struct gpiod_chip* chip_{nullptr};
    struct gpiod_line* line_{nullptr};
};

void setup_realtime_priority() noexcept {
    sched_param param{};
    param.sched_priority = 50;
    ::sched_setscheduler(0, SCHED_FIFO, &param);
    ::mlockall(MCL_CURRENT | MCL_FUTURE);
}

[[nodiscard]] std::uint16_t crc_accumulate(std::uint8_t byte, std::uint16_t crc) noexcept {
    std::uint8_t ch = byte ^ static_cast<std::uint8_t>(crc & 0x00FF);
    ch = static_cast<std::uint8_t>(ch ^ (ch << 4));
    return static_cast<std::uint16_t>((crc >> 8) ^ (static_cast<std::uint16_t>(ch) << 8) ^
                                     (static_cast<std::uint16_t>(ch) << 3) ^ (static_cast<std::uint16_t>(ch) >> 4));
}

[[nodiscard]] std::uint16_t calculate_mavlink_crc(std::span<const std::uint8_t> buffer, std::uint8_t crc_extra) noexcept {
    std::uint16_t crc = 0xFFFF;
    for (std::size_t i = 1; i < buffer.size(); ++i) { // без стартового байта 0xFD
        crc = crc_accumulate(buffer[i], crc);
    }
    crc = crc_accumulate(crc_extra, crc);
    return crc;
}

std::expected<FileDescriptor, std::error_code> open_serial(std::string_view dev, speed_t speed) {
    int fd = ::open(dev.data(), O_RDWR | O_NOCTTY | O_NONBLOCK);
    if (fd < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }
    struct termios tty{};
    if (::tcgetattr(fd, &tty) != 0) {
        ::close(fd);
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }
    cfmakeraw(&tty);
    cfsetispeed(&tty, speed);
    cfsetospeed(&tty, speed);
    tty.c_cflag |= (CLOCAL | CREAD);
    tty.c_cflag &= ~CRTSCTS;
    if (::tcsetattr(fd, TCSANOW, &tty) != 0) {
        ::close(fd);
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }
    return FileDescriptor(fd);
}

std::expected<FileDescriptor, std::error_code> open_unix_socket(std::string_view path) {
    ::unlink(path.data());
    int fd = ::socket(AF_UNIX, SOCK_DGRAM | SOCK_NONBLOCK, 0);
    if (fd < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }
    sockaddr_un addr{};
    addr.sun_family = AF_UNIX;
    std::strncpy(addr.sun_path, path.data(), sizeof(addr.sun_path) - 1);
    if (::bind(fd, reinterpret_cast<struct sockaddr*>(&addr), sizeof(addr)) < 0) {
        ::close(fd);
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }
    ::chmod(path.data(), 0666);
    return FileDescriptor(fd);
}

} // namespace companion

int main() {
    companion::setup_realtime_priority();

    auto serial_res = companion::open_serial(companion::kSerialPort, B921600);
    if (!serial_res) {
        std::cerr << "Помилка відкриття UART: " << serial_res.error().message() << '\n';
        return EXIT_FAILURE;
    }

    auto socket_res = companion::open_unix_socket(companion::kSocketPath);
    if (!socket_res) {
        std::cerr << "Помилка відкриття сокета: " << socket_res.error().message() << '\n';
        return EXIT_FAILURE;
    }

    auto serial_fd = std::move(*serial_res);
    auto sock_fd = std::move(*socket_res);
    companion::GpioLineGuard gpio(companion::kGpioChip, companion::kWatchdogPin);

    std::uint8_t seq = 0;
    int pin_state = 0;
    auto last_worker_ping = std::chrono::steady_clock::now();
    auto last_hb_time = std::chrono::steady_clock::now();
    auto last_strobe_time = std::chrono::steady_clock::now();

    std::cout << "C++23 Companion Watchdog запущено. Моніторинг активний.\n";

    while (true) {
        const auto now = std::chrono::steady_clock::now();

        // 1. Прийом сигналів активності від робочих потоків
        char buf[32];
        ssize_t bytes = ::recv(sock_fd.get(), buf, sizeof(buf) - 1, 0);
        if (bytes > 0) {
            buf[bytes] = '\0';
            if (std::string_view(buf, bytes).starts_with("ALIVE")) {
                last_worker_ping = now;
            }
        }

        const bool worker_healthy = (now - last_worker_ping) < companion::kProcessTimeout;

        // 2. Генерація стробу апаратного сторожа
        if (now - last_strobe_time >= companion::kStrobePeriod) {
            if (worker_healthy && gpio.available()) {
                pin_state = 1 - pin_state;
                gpio.set_level(pin_state);
            } else {
                gpio.set_level(0);
            }
            last_strobe_time = now;
        }

        // 3. Відправка пакета MAVLink HEARTBEAT
        if (now - last_hb_time >= companion::kHeartbeatPeriod) {
            companion::MavlinkV2HeartbeatPacket pkt{};
            pkt.seq = seq++;
            pkt.payload.system_status = worker_healthy ? 3 : 5; // 3=ACTIVE, 5=CRITICAL

            const auto pkt_span = std::span<const std::uint8_t>(
                reinterpret_cast<const std::uint8_t*>(&pkt),
                10 + sizeof(companion::MavlinkHeartbeatPayload)
            );
            pkt.checksum = companion::calculate_mavlink_crc(pkt_span, 50);

            ::write(serial_fd.get(), &pkt, sizeof(pkt));
            last_hb_time = now;
        }

        std::this_thread::sleep_for(10ms);
    }

    ::unlink(companion::kSocketPath.data());
    return EXIT_SUCCESS;
}
