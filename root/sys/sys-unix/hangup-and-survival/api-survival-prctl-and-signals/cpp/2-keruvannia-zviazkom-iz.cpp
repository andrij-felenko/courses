#include <sys/ioctl.h>
#include <termios.h>
#include <system_error>

namespace terminal_control {
    template <typename... Args>
    inline int terminal_ioctl(int fd, unsigned long request, Args... args) {
        int res = ::ioctl(fd, request, args...);
        if (res < 0) {
            throw std::system_error(errno, std::generic_category(), "ioctl terminal request failed");
        }
        return res;
    }
}
