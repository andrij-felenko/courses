#include <atomic>
#include <cstdint>

class AtomicEventCounter {
private:
    std::atomic<std::int64_t> counter{0};

public:
    void increment() {
        std::int64_t current = counter.load(std::memory_order_relaxed);
        while (!counter.compare_exchange_weak(current, current + 1,
                                            std::memory_order_release,
                                            std::memory_order_relaxed)) {
            // При невдачі current оновлюється актуальним значенням з пам'яті
        }
    }

    std::int64_t getValue() const {
        return counter.load(std::memory_order_acquire);
    }
};
