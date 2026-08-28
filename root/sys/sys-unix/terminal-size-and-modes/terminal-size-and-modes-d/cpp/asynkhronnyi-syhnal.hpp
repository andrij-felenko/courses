#include <csignal>
#include <atomic>

inline std::atomic<bool> g_window_resized{false};

extern "C" void handle_sigwinch(int) noexcept {
    g_window_resized.store(true, std::memory_order_relaxed);
}

void setup_signals() noexcept {
    struct sigaction sa{};
    sa.sa_handler = handle_sigwinch;
    sigemptyset(&sa.sa_mask);
    sa.sa_flags = SA_RESTART;
    ::sigaction(SIGWINCH, &sa, nullptr);
}
