#include <csignal>
#include <atomic>

class WindowResizeManager {
public:
    static void init() {
        struct sigaction sa{};
        sa.sa_handler = &WindowResizeManager::signal_handler;
        sigemptyset(&sa.sa_mask);
        sa.sa_flags = SA_RESTART;
        sigaction(SIGWINCH, &sa, nullptr);
    }

    [[nodiscard]] static bool is_resize_requested() noexcept {
        return resize_pending_.exchange(false, std::memory_order_relaxed);
    }

private:
    static inline std::atomic<bool> resize_pending_{false};

    static void signal_handler(int) noexcept {
        resize_pending_.store(true, std::memory_order_relaxed);
    }
};
