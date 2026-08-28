#include <csignal>
#include <atomic>
#include <unistd.h>
#include <sys/epoll.h>
#include <array>

namespace {
std::atomic<bool> g_terminate{false};

void signal_handler(int signo) noexcept {
    (void)signo;
    g_terminate.store(true, std::memory_order_relaxed);
}
} // namespace

int run_server(int epfd) {
    struct sigaction sa{};
    sa.sa_handler = signal_handler;
    sigemptyset(&sa.sa_mask);
    sa.sa_flags = 0;
    ::sigaction(SIGTERM, &sa, nullptr);

    std::array<epoll_event, 64> events{};
    while (!g_terminate.load(std::memory_order_relaxed)) {
        int nfds = ::epoll_wait(epfd, events.data(), static_cast<int>(events.size()), -1);
        if (nfds == -1) {
            continue;
        }
        /* Обробка вводу-виводу */
    }
    return 0;
}
