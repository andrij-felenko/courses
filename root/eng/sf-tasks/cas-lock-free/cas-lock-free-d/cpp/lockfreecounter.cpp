#include <atomic>
#include <cstdint>

class LockFreeCounter {
private:
    std::atomic<int64_t> value_{0};

public:
    explicit LockFreeCounter(int64_t initial = 0) : value_(initial) {}

    // Атомарний інкремент із довільним кроком через Read-Modify-CAS loop
    int64_t add(int64_t delta) {
        int64_t current = value_.load(std::memory_order_relaxed);

        // Цикл оптимістичного оновлення зі слабкою операцією CAS
        while (!value_.compare_exchange_weak(
            current, 
            current + delta,
            std::memory_order_release,
            std::memory_order_relaxed)) 
        {
            // У разі невдачі compare_exchange_weak записує актуальний стан пам'яті в current,
            // тому обчислення current + delta на наступній ітерації виконується над свіжими даними.
        }

        return current + delta;
    }

    int64_t get() const {
        return value_.load(std::memory_order_acquire);
    }
};
