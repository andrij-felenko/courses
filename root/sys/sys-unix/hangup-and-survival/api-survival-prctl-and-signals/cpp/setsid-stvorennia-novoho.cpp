#include <unistd.h>
#include <sys/types.h>
#include <system_error>

namespace process_control {
    inline pid_t create_session() {
        pid_t sid = ::setsid();
        if (sid < 0) {
            throw std::system_error(errno, std::generic_category(), "setsid failed");
        }
        return sid;
    }
}
