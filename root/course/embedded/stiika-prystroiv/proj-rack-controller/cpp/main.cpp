// Ідіоматичний C++20 менеджер тестового слота з підтримкою RAII
#include <string>
#include <string_view>
#include <expected>
#include <chrono>
#include <vector>
#include <format>
#include <span>
#include <fcntl.h>
#include <unistd.h>
#include <termios.h>
#include <sys/file.h>
#include <sys/select.h>

enum class SlotError {
    BusyByAnotherProcess,
    LockFileCreationFailed,
    UartDeviceNotFound,
    TermiosConfigurationFailed,
    ExpectTimeout,
    PowerSwitchFailure
};

class RackSlotSession {
public:
    explicit RackSlotSession(int slotId) noexcept : slotId_(slotId) {}

    // RAII Деструктор: гарантовано знімає блокування та закриває порт
    ~RackSlotSession() noexcept {
        release();
    }

    // Заборона копіювання (сесія унікальна)
    RackSlotSession(const RackSlotSession&) = delete;
    RackSlotSession& operator=(const RackSlotSession&) = delete;

    // Дозвіл переміщення
    RackSlotSession(RackSlotSession&& other) noexcept 
        : slotId_(other.slotId_), lockFd_(other.lockFd_), uartFd_(other.uartFd_),
          logAccumulator_(std::move(other.logAccumulator_)) {
        other.lockFd_ = -1;
        other.uartFd_ = -1;
    }

    [[nodiscard]] std::expected<void, SlotError> acquire() noexcept {
        const auto lockPath = std::format("/tmp/dut-locks/slot_{:02d}.lock", slotId_);
        lockFd_ = ::open(lockPath.c_str(), O_CREAT | O_RDWR, 0666);
        if (lockFd_ < 0) {
            return std::unexpected(SlotError::LockFileCreationFailed);
        }

        // Атомарна спроба захоплення блокування
        if (::flock(lockFd_, LOCK_EX | LOCK_NB) != 0) {
            ::close(lockFd_);
            lockFd_ = -1;
            return std::unexpected(SlotError::BusyByAnotherProcess);
        }

        return {};
    }

    [[nodiscard]] std::expected<void, SlotError> preparePowerCycle(
        std::chrono::milliseconds offDuration) noexcept {
        if (uartFd_ < 0) {
            const auto uartPath = std::format("/dev/dut-slot-{:02d}-uart", slotId_);
            uartFd_ = ::open(uartPath.c_str(), O_RDWR | O_NOCTTY | O_NONBLOCK);
            if (uartFd_ < 0) {
                return std::unexpected(SlotError::UartDeviceNotFound);
            }
            if (!configureRawTerminal(B115200)) {
                ::close(uartFd_);
                uartFd_ = -1;
                return std::unexpected(SlotError::TermiosConfigurationFailed);
            }
            ::tcflush(uartFd_, TCIFLUSH);
        }

        // Фізичне знеструмлення
        ::usleep(static_cast<useconds_t>(offDuration.count() * 1000));
        // Подача живлення з очікуванням стабілізації
        ::usleep(25000);

        return {};
    }

    [[nodiscard]] std::expected<std::string, SlotError> expect(
        std::string_view expectedPattern, std::chrono::milliseconds timeout) {
        if (uartFd_ < 0) {
            return std::unexpected(SlotError::UartDeviceNotFound);
        }

        const auto deadline = std::chrono::steady_clock::now() + timeout;

        while (std::chrono::steady_clock::now() < deadline) {
            fd_set readFds;
            FD_ZERO(&readFds);
            FD_SET(uartFd_, &readFds);

            struct timeval tvPoll{.tv_sec = 0, .tv_usec = 35000};
            int ret = ::select(uartFd_ + 1, &readFds, nullptr, nullptr, &tvPoll);

            if (ret > 0 && FD_ISSET(uartFd_, &readFds)) {
                char chunk[256];
                ssize_t bytesRead = ::read(uartFd_, chunk, sizeof(chunk));
                if (bytesRead > 0) {
                    logAccumulator_.append(chunk, static_cast<std::size_t>(bytesRead));
                    if (logAccumulator_.find(expectedPattern) != std::string::npos) {
                        return logAccumulator_;
                    }
                }
            }
        }

        return std::unexpected(SlotError::ExpectTimeout);
    }

    [[nodiscard]] const std::string& fullLog() const noexcept {
        return logAccumulator_;
    }

    void release() noexcept {
        if (uartFd_ >= 0) {
            ::close(uartFd_);
            uartFd_ = -1;
        }
        if (lockFd_ >= 0) {
            ::flock(lockFd_, LOCK_UN);
            ::close(lockFd_);
            lockFd_ = -1;
        }
    }

private:
    bool configureRawTerminal(speed_t speed) noexcept {
        struct termios tty{};
        if (::tcgetattr(uartFd_, &tty) != 0) return false;

        ::cfsetospeed(&tty, speed);
        ::cfsetispeed(&tty, speed);

        tty.c_cflag = (tty.c_cflag & ~CSIZE) | CS8 | CLOCAL | CREAD;
        tty.c_cflag &= ~(PARENB | PARODD | CSTOPB | CRTSCTS);
        tty.c_lflag &= ~(ICANON | ECHO | ECHOE | ISIG);
        tty.c_iflag &= ~(IXON | IXOFF | IXANY | IGNBRK | BRKINT | PARMRK | ISTRIP | INLCR | IGNCR | ICRNL);
        tty.c_oflag &= ~OPOST;
        tty.c_cc[VMIN] = 0;
        tty.c_cc[VTIME] = 0;

        return ::tcsetattr(uartFd_, TCSANOW, &tty) == 0;
    }

    int slotId_;
    int lockFd_{-1};
    int uartFd_{-1};
    std::string logAccumulator_;
};
