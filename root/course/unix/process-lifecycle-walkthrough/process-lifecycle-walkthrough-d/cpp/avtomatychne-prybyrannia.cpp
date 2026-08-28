#include <csignal>
#include <cstddef>
#include <system_error>

void disable_zombies() {
    struct sigaction sa{};
    sa.sa_handler = SIG_IGN;
    ::sigemptyset(&sa.sa_mask);
    sa.sa_flags = SA_NOCLDWAIT; // автоматичне прибирання зомбі ядром
    if (::sigaction(SIGCHLD, &sa, nullptr) == -1) {
        throw std::system_error(errno, std::generic_category(), "sigaction failed");
    }
}
