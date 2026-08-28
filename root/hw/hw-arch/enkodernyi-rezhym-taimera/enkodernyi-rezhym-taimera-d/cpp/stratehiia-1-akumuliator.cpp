#include <cstdint>
#include <atomic>

class OverflowTracker {
public:
    static inline std::atomic<int32_t> overflow_count{0};

    static void handle_timer_irq(TimerHardware& tim) noexcept {
        if (tim.SR & (1U << 0)) { // Перевірка прапорця UIF
            tim.SR = ~(1U << 0);  // Скидання прапорця UIF
            if ((tim.CR1 & (1U << 4)) == 0) {
                overflow_count.fetch_add(1, std::memory_order_relaxed);
            } else {
                overflow_count.fetch_sub(1, std::memory_order_relaxed);
            }
        }
    }
};
