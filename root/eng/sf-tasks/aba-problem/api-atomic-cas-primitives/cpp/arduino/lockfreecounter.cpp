#include <Arduino.h>
#include <atomic>

class LockFreeCounter {
private:
    std::atomic<uint32_t> counter;

public:
    explicit LockFreeCounter(uint32_t initial = 0) : counter(initial) {}

    // Безблокове накопичення значення без використання спінлоків
    uint32_t add(uint32_t value) {
        uint32_t expected = counter.load(std::memory_order_relaxed);

        // Слабкий CAS у зовнішньому циклі виключає зайві апаратні інструкції
        while (!counter.compare_exchange_weak(
            expected,
            expected + value,
            std::memory_order_release,
            std::memory_order_relaxed
        )) {
            // Змінна expected автоматично оновлюється поточним значенням при невдачі
        }

        return expected + value;
    }

    uint32_t get() const {
        return counter.load(std::memory_order_acquire);
    }
};
