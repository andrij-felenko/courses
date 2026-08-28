// Системні виклики керування сигналом Break на мові C++20
#include <termios.h>
#include <sys/ioctl.h>
#include <unistd.h>
#include <system_error>

namespace serial_api {

inline void send_break(int fd, int duration = 0) {
    if (::tcsendbreak(fd, duration) != 0) {
        throw std::system_error(errno, std::generic_category(), "tcsendbreak failed");
    }
}

inline void set_break_state(int fd, bool active) {
    const unsigned long request = active ? TIOCSBRK : TIOCCBRK;
    if (::ioctl(fd, request) != 0) {
        throw std::system_error(errno, std::generic_category(), "ioctl break request failed");
    }
}

} // namespace serial_api
