#include <csignal>
#include <unistd.h>
#include <atomic>
#include <string_view>
#include <memory>
#include <iostream>

namespace {
    std::atomic<int> g_signal_pending{0};

    extern "C" void signal_dispatcher(int sig) noexcept {
        g_signal_pending.store(sig, std::memory_order_relaxed);
        constexpr std::string_view msg = "Сигнал перехоплено, планується завершення...\n";
        [[maybe_unused]] auto _ = write(STDERR_FILENO, msg.data(), msg.size());
    }
}

class SignalManager {
public:
    SignalManager() {
        struct sigaction sa{};
        sa.sa_handler = signal_dispatcher;
        sigemptyset(&sa.sa_mask);
        sa.sa_flags = 0;

        sigaction(SIGINT, &sa, nullptr);
        sigaction(SIGTERM, &sa, nullptr);
    }

    [[nodiscard]] static int get_pending_signal() noexcept {
        return g_signal_pending.load(std::memory_order_relaxed);
    }
};
