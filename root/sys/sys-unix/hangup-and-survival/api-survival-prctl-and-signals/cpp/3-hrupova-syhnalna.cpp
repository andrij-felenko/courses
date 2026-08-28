#include <csignal>
#include <system_error>

namespace signal_control {
    inline void send_group_signal(pid_t pgrp, int sig) {
        if (::killpg(pgrp, sig) < 0) {
            throw std::system_error(errno, std::generic_category(), "killpg failed");
        }
    }
}
