#include <atomic>
#include <cstdint>

class LockFreeCounter {
private:
    std::atomic<uint32_t> value_{0};

public:
    // Атомарне множення значення лічильника в циклі CAS
    uint32_t multiply(uint32_t factor) noexcept {
        uint32_t expected = value_.load(std::memory_order_relaxed);
        uint32_t desired;

        do {
            desired = expected * factor;
            // Слабкий CAS оптимізує генерацію коду для ARM/RISC-V всередині циклу
        } while (!value_.compare_exchange_weak(expected, desired,
                                               std::memory_order_acq_rel,
                                               std::memory_order_relaxed));

        return desired;
    }

    uint32_t get() const noexcept {
        return value_.load(std::memory_order_acquire);
    }
};
