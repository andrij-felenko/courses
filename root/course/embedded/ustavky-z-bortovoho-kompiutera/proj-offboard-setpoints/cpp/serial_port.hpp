#pragma once

#include <cerrno>
#include <chrono>
#include <cstdint>
#include <expected>
#include <span>
#include <string>
#include <system_error>
#include <utility>

#include <fcntl.h>
#include <poll.h>
#include <termios.h>
#include <unistd.h>

// UART у «сирому» режимі. Дескриптор живе рівно стільки, скільки об'єкт:
// жодного close() у гілках помилок — цим займається деструктор.
class SerialPort {
public:
    SerialPort(const std::string& port, speed_t baud) {
        fd_ = ::open(port.c_str(), O_RDWR | O_NOCTTY | O_NONBLOCK);
        if (fd_ < 0) {
            throw std::system_error(errno, std::system_category(), "open " + port);
        }

        termios tty{};
        if (::tcgetattr(fd_, &tty) != 0) {
            fail("tcgetattr");
        }
        // MAVLink двійковий: канонізація, ехо й підміна CR/LF псують кадр.
        ::cfmakeraw(&tty);
        if (::cfsetispeed(&tty, baud) != 0 || ::cfsetospeed(&tty, baud) != 0) {
            fail("cfsetspeed");
        }
        tty.c_cflag |= (CLOCAL | CREAD);
        tty.c_cflag &= ~CRTSCTS;  // телеметричний джгут без RTS/CTS
        tty.c_cc[VMIN] = 0;
        tty.c_cc[VTIME] = 0;
        if (::tcsetattr(fd_, TCSANOW, &tty) != 0) {
            fail("tcsetattr");
        }
        // Недорозібраний хвіст чужого кадру збив би парсер на старті.
        ::tcflush(fd_, TCIOFLUSH);
    }

    ~SerialPort() {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    SerialPort(const SerialPort&) = delete;
    SerialPort& operator=(const SerialPort&) = delete;
    SerialPort(SerialPort&& other) noexcept : fd_(std::exchange(other.fd_, -1)) {}

    // Помилка запису — очікувана подія на кожному такті, а не виняток:
    // викликач її рахує й далі шле наступну уставку.
    [[nodiscard]] std::expected<void, std::error_code>
    write_all(std::span<const std::uint8_t> data, std::chrono::milliseconds timeout) {
        const auto deadline = std::chrono::steady_clock::now() + timeout;
        std::size_t sent = 0;

        while (sent < data.size()) {
            const ssize_t n = ::write(fd_, data.data() + sent, data.size() - sent);
            if (n > 0) {
                sent += static_cast<std::size_t>(n);
                continue;
            }
            if (n < 0 && errno == EINTR) {
                continue;
            }
            if (n < 0 && errno != EAGAIN && errno != EWOULDBLOCK) {
                return std::unexpected(std::error_code(errno, std::system_category()));
            }

            // Буфер драйвера повний — чекаємо на місце, але не довше дедлайну:
            // повільний UART не має права з'їдати такт циклу 20 Гц.
            const auto left = std::chrono::duration_cast<std::chrono::milliseconds>(
                deadline - std::chrono::steady_clock::now());
            if (left.count() <= 0) {
                return std::unexpected(std::make_error_code(std::errc::timed_out));
            }
            pollfd pfd{fd_, POLLOUT, 0};
            const int r = ::poll(&pfd, 1, static_cast<int>(left.count()));
            if (r < 0 && errno == EINTR) {
                continue;
            }
            if (r < 0) {
                return std::unexpected(std::error_code(errno, std::system_category()));
            }
            if (r == 0) {
                return std::unexpected(std::make_error_code(std::errc::timed_out));
            }
        }
        return {};
    }

    // Забирає те, що вже прийшло. Порожній span — даних немає.
    [[nodiscard]] std::span<std::uint8_t> read_some(std::span<std::uint8_t> buf) {
        for (;;) {
            const ssize_t n = ::read(fd_, buf.data(), buf.size());
            if (n >= 0) {
                return buf.first(static_cast<std::size_t>(n));
            }
            if (errno == EINTR) {
                continue;
            }
            if (errno == EAGAIN || errno == EWOULDBLOCK) {
                return buf.first(0);
            }
            throw std::system_error(errno, std::system_category(), "read(uart)");
        }
    }

private:
    [[noreturn]] void fail(const char* what) {
        const int saved = errno;
        ::close(fd_);
        fd_ = -1;
        throw std::system_error(saved, std::system_category(), what);
    }

    int fd_{-1};
};
