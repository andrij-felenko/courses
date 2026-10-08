#include <termios.h>
#include <fcntl.h>
#include <unistd.h>
#include <stdexcept>
#include <string>

class VCPTerminalPort {
private:
    int fd_ = -1;

public:
    explicit VCPTerminalPort(const std::string& port_path) {
        fd_ = ::open(port_path.c_str(), O_RDWR | O_NOCTTY | O_NDELAY);
        if (fd_ < 0) {
            throw std::runtime_error("Не вдалося відкрити VCP порт: " + port_path);
        }

        struct termios tty{};
        if (::tcgetattr(fd_, &tty) != 0) {
            ::close(fd_);
            throw std::runtime_error("Помилка зчитування атрибутів termios");
        }

        /* Налаштування швидкості 115200 baud */
        ::cfsetispeed(&tty, B115200);
        ::cfsetospeed(&tty, B115200);

        /* Конфігурація кадру 8N1 */
        tty.c_cflag &= ~PARENB;
        tty.c_cflag &= ~CSTOPB;
        tty.c_cflag &= ~CSIZE;
        tty.c_cflag |= CS8;
        tty.c_cflag |= (CLOCAL | CREAD);

        /* Вимкнення апаратного керування потоком */
        tty.c_cflag &= ~CRTSCTS;
        tty.c_iflag &= ~(IXON | IXOFF | IXANY);

        /* Сирий режим прийому даних */
        tty.c_lflag &= ~(ICANON | ECHO | ECHOE | ISIG);
        tty.c_oflag |= ONLCR;

        if (::tcsetattr(fd_, TCSANOW, &tty) != 0) {
            ::close(fd_);
            throw std::runtime_error("Помилка застосування налаштувань termios");
        }
    }

    ~VCPTerminalPort() {
        if (fd_ >= 0) ::close(fd_);
    }
};
