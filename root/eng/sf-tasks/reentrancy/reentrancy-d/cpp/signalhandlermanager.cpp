#include <iostream>
#include <csignal>
#include <atomic>
#include <unistd.h>

// НЕБЕЗПЕЧНИЙ ВАРІАНТ (C++): використання std::cout у сигнальному контексті
std::atomic<uint64_t> g_events_unsafe{0};

void unsafe_handler_cpp(int sig) {
    // ПОМИЛКА: std::cout використовує спільні буфери виводу та м'ютекси
    std::cout << "Отримано сигнал: " << sig << std::endl;
}

// БЕЗПЕЧНИЙ ВАРІАНТ (C++): lock-free atomic прапорець та системний виклик write
class SignalHandlerManager {
public:
    static inline std::atomic_flag signal_received = ATOMIC_FLAG_INIT;

    static void safe_handler(int sig) {
        (void)sig;
        // test_and_set є lock-free атомарною операцією
        signal_received.test_and_set(std::memory_order_relaxed);
    }
};

int main() {
    struct sigaction sa{};
    sa.sa_handler = SignalHandlerManager::safe_handler;
    sigemptyset(&sa.sa_mask);
    sa.sa_flags = 0;

    sigaction(SIGINT, &sa, nullptr);

    const char msg[] = "C++: Очікування асинхронного переривання...\n";
    ::write(STDOUT_FILENO, msg, sizeof(msg) - 1);

    while (!SignalHandlerManager::signal_received.test(std::memory_order_relaxed)) {
        ::usleep(100000);
    }

    const char done[] = "C++: Сигнал безпечно зчитано в основному потоці!\n";
    ::write(STDOUT_FILENO, done, sizeof(done) - 1);

    return 0;
}
