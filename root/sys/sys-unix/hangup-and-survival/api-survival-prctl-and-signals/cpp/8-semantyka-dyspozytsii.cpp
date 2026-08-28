#include <csignal>
#include <system_error>

namespace signal_control {
    inline void set_signal_action(int signum, const struct sigaction& act, struct sigaction* oldact = nullptr) {
        if (::sigaction(signum, &act, oldact) < 0) {
            throw std::system_error(errno, std::generic_category(), "sigaction failed");
        }
    }
}
