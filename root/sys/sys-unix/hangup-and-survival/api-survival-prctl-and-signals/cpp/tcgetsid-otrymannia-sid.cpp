#include <termios.h>
#include <unistd.h>
#include <system_error>

namespace terminal_control {
    inline pid_t get_terminal_session(int fd) {
        pid_t sid = ::tcgetsid(fd);
        if (sid < 0) {
            throw std::system_error(errno, std::generic_category(), "tcgetsid failed");
        }
        return sid;
    }
}
