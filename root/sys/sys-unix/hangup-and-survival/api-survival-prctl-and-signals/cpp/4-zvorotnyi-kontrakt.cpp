#include <sys/prctl.h>
#include <csignal>
#include <unistd.h>
#include <system_error>

namespace process_safety {

void enable_parent_death_signal(int signum) {
    if (::prctl(PR_SET_PDEATHSIG, signum) < 0) {
        throw std::system_error(errno, std::generic_category(), "prctl PR_SET_PDEATHSIG failed");
    }
    // Захист від стану гонитви (race condition), якщо батьківський процес помер до prctl
    if (::getppid() == 1) {
        ::kill(::getpid(), signum);
    }
}

} // namespace process_safety
