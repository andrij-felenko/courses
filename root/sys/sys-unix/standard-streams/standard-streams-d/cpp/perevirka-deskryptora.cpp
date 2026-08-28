#include <iostream>
#include <unistd.h>
#include <sys/ioctl.h>
#include <termios.h>
#include <cerrno>

bool is_device_terminal(int fd) noexcept {
    ::termios t{};
    if (::ioctl(fd, TCGETS, &t) == 0) {
        return true;
    }
    return false;
}
