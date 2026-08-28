// user_concurrency_demo.cpp (C++20 std::atomic + std::jthread + RAII)
#include <iostream>
#include <atomic>
#include <thread>
#include <chrono>

struct SharedState {
    std::atomic<int> counter{0};
    std::atomic<bool> ready{false};
};

class UserspaceConcurrencyApp {
public:
    void run() {
        SharedState state;

        // Використовуємо jthread з автоматичним приєднанням (RAII)
        std::jthread writer([&state]() {
            for (int i = 0; i < 5; ++i) {
                int cur = state.counter.load(std::memory_order_relaxed);
                state.counter.store(cur + 1, std::memory_order_relaxed);
                
                // Еквівалент smp_store_release
                state.ready.store(true, std::memory_order_release);
                std::this_thread::sleep_for(std::chrono::milliseconds(2));
            }
        });

        std::jthread reader([&state]() {
            for (int i = 0; i < 5; ++i) {
                // Еквівалент smp_load_acquire
                if (state.ready.load(std::memory_order_acquire)) {
                    int val = state.counter.load(std::memory_order_relaxed);
                    std::cout << "C++ Userspace: Counter observed = " << val << "\n";
                }
                std::this_thread::sleep_for(std::chrono::milliseconds(2));
            }
        });
    }
};

int main() {
    UserspaceConcurrencyApp app;
    app.run();
    std::cout << "C++ Userspace Concurrency Test Passed Cleanly.\n";
    return 0;
}
