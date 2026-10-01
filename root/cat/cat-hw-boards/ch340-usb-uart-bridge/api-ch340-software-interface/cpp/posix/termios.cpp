#include <fcntl.h>
#include <unistd.h>
#include <termios.h>
#include <system_error>
#include <string>

int open_ch340_port(const std::string &port_path) {
    int fd = ::open(port_path.c_str(), O_RDWR | O_NOCTTY | O_NDELAY);
    if (fd < 0) {
        throw std::system_error(errno, std::generic_category(), 
                               "Не вдалося ініціалізувати Virtual COM Port CH340");
    }
    ::fcntl(fd, F_SETFL, 0);

    struct termios options{};
    if (::tcgetattr(fd, &options) == 0) {
        options.c_cc[VMIN] = 0;   // Не чекати мінімальної кількості байтів
        options.c_cc[VTIME] = 10; // Таймаут 1.0 секунда
        ::tcsetattr(fd, TCSANOW, &options);
    }
    return fd;
}
