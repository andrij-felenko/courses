// posix_break_demo.cpp - ООП-обгортка послідовного порту з підтримкою Break на C++
#include <iostream>
#include <string>
#include <vector>
#include <stdexcept>
#include <span>
#include <chrono>
#include <thread>
#include <fcntl.h>
#include <unistd.h>
#include <termios.h>
#include <sys/ioctl.h>

class SerialPort {
public:
    explicit SerialPort(const std::string& dev, speed_t baud = B115200) {
        fd_ = ::open(dev.c_str(), O_RDWR | O_NOCTTY | O_NONBLOCK);
        if (fd_ < 0) {
            throw std::runtime_error("Не вдалося відкрити послідовний порт: " + dev);
        }

        struct termios tty{};
        if (::tcgetattr(fd_, &tty) != 0) {
            ::close(fd_);
            throw std::runtime_error("Помилка tcgetattr");
        }

        ::cfsetospeed(&tty, baud);
        ::cfsetispeed(&tty, baud);

        tty.c_cflag = (tty.c_cflag & ~CSIZE) | CS8;
        tty.c_cflag |= (CLOCAL | CREAD);
        tty.c_cflag &= ~(PARENB | PARODD | CSTOPB | CRTSCTS);

        // Налаштування прапорців: виловлювати Break через префікс PARMRK
        tty.c_iflag &= ~(IGNBRK | BRKINT | IGNPAR | INLCR | ICRNL | IXON | IXOFF);
        tty.c_iflag |= PARMRK;
        tty.c_lflag = 0;
        tty.c_oflag = 0;

        if (::tcsetattr(fd_, TCSANOW, &tty) != 0) {
            ::close(fd_);
            throw std::runtime_error("Помилка tcsetattr");
        }
    }

    ~SerialPort() noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    // Заборона копіювання (RAII-ресурс)
    SerialPort(const SerialPort&) = delete;
    SerialPort& operator=(const SerialPort&) = delete;

    // Дозвіл переміщення
    SerialPort(SerialPort&& other) noexcept : fd_{other.fd_} {
        other.fd_ = -1;
    }
    SerialPort& operator=(SerialPort&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    void send_break() const {
        if (::tcsendbreak(fd_, 0) != 0) {
            throw std::runtime_error("Помилка tcsendbreak");
        }
    }

    [[nodiscard]] std::vector<uint8_t> read_bytes(size_t max_count = 256) const {
        std::vector<uint8_t> buffer(max_count);
        const ssize_t n = ::read(fd_, buffer.data(), max_count);
        if (n <= 0) {
            return {};
        }
        buffer.resize(static_cast<size_t>(n));
        return buffer;
    }

private:
    int fd_{-1};
};

int main(int argc, char* argv[]) {
    try {
        const std::string port = (argc > 1) ? argv[1] : "/dev/ttyUSB0";
        SerialPort serial{port};

        std::cout << "Порт " << port << " відкрито. Надсилаємо сигнал Break...\n";
        serial.send_break();
        std::cout << "Break надіслано. Очікуємо відповіді...\n";

        for (int i = 0; i < 50; ++i) {
            auto data = serial.read_bytes();
            if (!data.empty()) {
                std::span<const uint8_t> s{data};
                for (size_t idx = 0; idx < s.size(); ++idx) {
                    if (idx + 2 < s.size() && s[idx] == 0xFF && s[idx + 1] == 0x00 && s[idx + 2] == 0x00) {
                        std::cout << ">>> [ВИЯВЛЕНО BREAK CONDITION НА ЛІНІЇ RX!]\n";
                        idx += 2;
                    } else {
                        std::cout << "Дані: 0x" << std::hex << static_cast<int>(s[idx]) << std::dec << "\n";
                    }
                }
            }
            std::this_thread::sleep_for(std::chrono::milliseconds(50));
        }
    } catch (const std::exception& e) {
        std::cerr << "Помилка: " << e.what() << "\n";
        return EXIT_FAILURE;
    }
    return EXIT_SUCCESS;
}
