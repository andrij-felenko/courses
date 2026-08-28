#include <termios.h>
#include <unistd.h>
#include <system_error>

std::error_code enable_hangup_on_close(int fd) noexcept {
    termios tty{};
    if (::tcgetattr(fd, &tty) < 0) {
        return std::error_code(errno, std::generic_category());
    }
    tty.c_cflag |= HUPCL;
    if (::tcsetattr(fd, TCSANOW, &tty) < 0) {
        return std::error_code(errno, std::generic_category());
    }
    return {};
}
