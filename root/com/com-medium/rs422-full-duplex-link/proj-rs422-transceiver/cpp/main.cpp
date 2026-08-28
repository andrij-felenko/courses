#include <iostream>
#include <span>
#include <string_view>
#include <system_error>
#include <expected>
#include <vector>
#include <cstdint>
#include <cstring>
#include <unistd.h>
#include <fcntl.h>
#include <termios.h>

class Rs422Port {
public:
    Rs422Port() noexcept : fd_{-1} {}
    ~Rs422Port() noexcept { close(); }

    Rs422Port(const Rs422Port&) = delete;
    Rs422Port& operator=(const Rs422Port&) = delete;

    Rs422Port(Rs422Port&& other) noexcept : fd_{other.fd_} {
        other.fd_ = -1;
    }

    Rs422Port& operator=(Rs422Port&& other) noexcept {
        if (this != &other) {
            close();
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    // Відкриття та налаштування порту RS-422 з використанням RAII
    static std::expected<Rs422Port, std::error_code> open_port(
        std::string_view path, speed_t baud_rate = B115200) noexcept 
    {
        int fd = ::open(path.data(), O_RDWR | O_NOCTTY | O_NDELAY);
        if (fd < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        ::fcntl(fd, F_SETFL, 0);

        termios tty{};
        if (::tcgetattr(fd, &tty) != 0) {
            auto err = std::error_code(errno, std::generic_category());
            ::close(fd);
            return std::unexpected(err);
        }

        ::cfsetispeed(&tty, baud_rate);
        ::cfsetospeed(&tty, baud_rate);

        // Режим 8N1 (8 бітів, без парності, 1 стоп-біт)
        tty.c_cflag &= ~PARENB;
        tty.c_cflag &= ~CSTOPB;
        tty.c_cflag &= ~CSIZE;
        tty.c_cflag |= CS8;
        tty.c_cflag &= ~CRTSCTS;
        tty.c_cflag |= (CLOCAL | CREAD);

        tty.c_lflag &= ~(ICANON | ECHO | ECHOE | ISIG);
        tty.c_iflag &= ~(IXON | IXOFF | IXANY | IGNBRK | BRKINT | PARMRK | ISTRIP | INLCR | IGNCR | ICRNL);
        tty.c_oflag &= ~OPOST;

        tty.c_cc[VMIN] = 0;
        tty.c_cc[VTIME] = 1; // 100 мс

        if (::tcsetattr(fd, TCSANOW, &tty) != 0) {
            auto err = std::error_code(errno, std::generic_category());
            ::close(fd);
            return std::unexpected(err);
        }

        ::tcflush(fd, TCIOFLUSH);
        Rs422Port port;
        port.fd_ = fd;
        return port;
    }

    void close() noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
            fd_ = -1;
        }
    }

    [[nodiscard]] bool is_open() const noexcept { return fd_ >= 0; }

    // Відправка буфера у лінію передачі
    std::expected<size_t, std::error_code> send(std::span<const uint8_t> data) noexcept {
        size_t total_sent = 0;
        while (total_sent < data.size()) {
            ssize_t res = ::write(fd_, data.data() + total_sent, data.size() - total_sent);
            if (res < 0) {
                if (errno == EINTR) continue;
                return std::unexpected(std::error_code(errno, std::generic_category()));
            }
            total_sent += static_cast<size_t>(res);
        }
        return total_sent;
    }

    // Прийом даних із лінії у наданий буфер
    std::expected<size_t, std::error_code> receive(std::span<uint8_t> buffer) noexcept {
        ssize_t res = ::read(fd_, buffer.data(), buffer.size());
        if (res < 0) {
            if (errno == EINTR) return 0;
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }
        return static_cast<size_t>(res);
    }

private:
    int fd_;
};
