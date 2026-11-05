#include <atomic>
#include <cstdint>
#include "FreeRTOS.h"
#include "task.h"

class LockFreeCounter {
public:
    explicit LockFreeCounter(uint32_t initial = 0) : value_(initial) {}

    uint32_t add(uint32_t val) noexcept {
        uint32_t current = value_.load(std::memory_order_relaxed);
        uint32_t backoff = 1;

        constexpr uint32_t max_backoff = 64;

        while (!value_.compare_exchange_weak(current,
                                             current + val,
                                             std::memory_order_release,
                                             std::memory_order_relaxed)) {
            // Оптимізація паузи для зменшення колізій у кеш-рядку
            for (uint32_t i = 0; i < backoff; ++i) {
                asm volatile("nop");
            }
            if (backoff < max_backoff) {
                backoff <<= 1;
            }
        }
        return current + val;
    }

    uint32_t get() const noexcept {
        return value_.load(std::memory_order_acquire);
    }

private:
    std::atomic<uint32_t> value_;
};
