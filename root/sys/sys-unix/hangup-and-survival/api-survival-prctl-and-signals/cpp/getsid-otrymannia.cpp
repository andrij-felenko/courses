#include <unistd.h>
#include <sys/types.h>
#include <system_error>

namespace process_control {
    inline pid_t get_session_id(pid_t pid = 0) {
        pid_t sid = ::getsid(pid);
        if (sid < 0) {
            throw std::system_error(errno, std::generic_category(), "getsid failed");
        }
        return sid;
    }
}
