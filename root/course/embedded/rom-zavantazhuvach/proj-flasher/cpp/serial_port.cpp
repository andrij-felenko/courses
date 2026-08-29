#include "serial_port.hpp"

#include <cerrno>
#include <system_error>
#include <thread>
#include <utility>

#include <fcntl.h>
#include <poll.h>
#include <sys/ioctl.h>
#include <termios.h>
#include <unistd.h>

namespace {

[[noreturn]] void throwErrno(const std::string& what)
{
    throw std::system_error(errno, std::generic_category(), what);
}

} // namespace

SerialPort::SerialPort(const std::string& path)
{
    fd_ = ::open(path.c_str(), O_RDWR | O_NOCTTY);
    if (fd_ < 0) {
        throwErrno("не відкривається " + path);
    }

    termios tty{};
    if (::tcgetattr(fd_, &tty) != 0) {
        const int saved = errno;
        ::close(fd_);
        fd_ = -1;
        throw std::system_error(saved, std::generic_category(), "tcgetattr " + path);
    }

    ::cfsetispeed(&tty, B115200);
    ::cfsetospeed(&tty, B115200);

    tty.c_cflag = (tty.c_cflag & ~static_cast<tcflag_t>(CSIZE)) | CS8; // 8 бітів даних
    tty.c_cflag |= PARENB;                                             // парність увімкнена
    tty.c_cflag &= ~static_cast<tcflag_t>(PARODD);                     // саме Even: кадр 8E1
    tty.c_cflag &= ~static_cast<tcflag_t>(CSTOPB);                     // рівно 1 стоп-біт
    tty.c_cflag &= ~static_cast<tcflag_t>(CRTSCTS);                    // DTR/RTS потрібні як GPIO
    tty.c_cflag |= (CLOCAL | CREAD);

    // Двійковий потік: жодних XON/XOFF, інакше байт 0x13 усередині образу
    // зупинить передачу на рівні ядра.
    tty.c_iflag &= ~static_cast<tcflag_t>(IXON | IXOFF | IXANY | INLCR | ICRNL | IGNCR | ISTRIP | BRKINT);
    tty.c_iflag |= INPCK;
    tty.c_oflag = 0;
    tty.c_lflag = 0; // не канонічний режим, без ECHO і без ISIG

    tty.c_cc[VMIN] = 0;
    tty.c_cc[VTIME] = 10; // 1.0 с посимвольно — read() не зависає назавжди

    if (::tcsetattr(fd_, TCSANOW, &tty) != 0) {
        const int saved = errno;
        ::close(fd_);
        fd_ = -1;
        throw std::system_error(saved, std::generic_category(), "tcsetattr " + path);
    }

    ::tcflush(fd_, TCIOFLUSH);
}

SerialPort::~SerialPort()
{
    if (fd_ >= 0) {
        ::close(fd_);
    }
}

SerialPort::SerialPort(SerialPort&& other) noexcept : fd_{std::exchange(other.fd_, -1)} {}

SerialPort& SerialPort::operator=(SerialPort&& other) noexcept
{
    if (this != &other) {
        if (fd_ >= 0) {
            ::close(fd_);
        }
        fd_ = std::exchange(other.fd_, -1);
    }
    return *this;
}

bool SerialPort::write(std::span<const std::uint8_t> data) const
{
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
        return false;
    }
    // Далі ми одразу слухаємо відповідь, тож чекаємо, поки байти підуть у лінію.
    return ::tcdrain(fd_) == 0;
}

bool SerialPort::read(std::span<std::uint8_t> buffer, std::chrono::milliseconds timeout) const
{
    const auto deadline = std::chrono::steady_clock::now() + timeout;
    std::size_t got = 0;

    while (got < buffer.size()) {
        const auto now = std::chrono::steady_clock::now();
        if (now >= deadline) {
            return false;
        }

        const auto left = std::chrono::duration_cast<std::chrono::milliseconds>(deadline - now);
        pollfd pfd{.fd = fd_, .events = POLLIN, .revents = 0};

        const int ready = ::poll(&pfd, 1, static_cast<int>(left.count()));
        if (ready < 0) {
            if (errno == EINTR) {
                continue;
            }
            return false;
        }
        if (ready == 0) {
            return false; // завантажувач мовчить
        }

        const ssize_t n = ::read(fd_, buffer.data() + got, buffer.size() - got);
        if (n > 0) {
            got += static_cast<std::size_t>(n);
            continue;
        }
        if (n == 0 || errno == EINTR || errno == EAGAIN) {
            continue; // спрацював VTIME, час іще лишився
        }
        return false;
    }
    return true;
}

void SerialPort::flush() const noexcept
{
    ::tcflush(fd_, TCIOFLUSH);
}

// DTR і RTS керують двома транзисторами: Q1 тримає NRST, Q2 — BOOT0.
void SerialPort::setLines(bool dtr, bool rts) const
{
    int bits = 0;
    if (::ioctl(fd_, TIOCMGET, &bits) < 0) {
        throwErrno("TIOCMGET");
    }
    if (dtr) {
        bits |= TIOCM_DTR;
    } else {
        bits &= ~TIOCM_DTR;
    }
    if (rts) {
        bits |= TIOCM_RTS;
    } else {
        bits &= ~TIOCM_RTS;
    }
    if (::ioctl(fd_, TIOCMSET, &bits) < 0) {
        throwErrno("TIOCMSET");
    }
}

void SerialPort::enterBootloader() const
{
    using namespace std::chrono_literals;

    // DTR = 0, RTS = 1 — відкривається Q2, BOOT0 підтягується до VCC,
    // конденсатор на цьому піні набирає заряд.
    setLines(false, true);
    std::this_thread::sleep_for(20ms);

    // DTR = 1, RTS = 0 — відкривається Q1, NRST притиснуто до землі.
    setLines(true, false);
    std::this_thread::sleep_for(80ms);

    // Обидві лінії в нуль: скидання відпущено, BOOT0 тримає заряд.
    setLines(false, false);

    // Ядру потрібен час на HSI і старт System Memory; раніший 0x7F пропаде.
    std::this_thread::sleep_for(100ms);
    flush();
}
