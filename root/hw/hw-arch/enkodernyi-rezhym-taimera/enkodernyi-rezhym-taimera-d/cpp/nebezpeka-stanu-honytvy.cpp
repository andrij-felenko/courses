#include <cstdint>
#include <atomic>

int64_t get_atomic_position(const TimerHardware& tim, const std::atomic<int32_t>& overflow_cnt) noexcept {
    int32_t high1{0}, high2{0};
    uint16_t low{0};
    do {
        high1 = overflow_cnt.load(std::memory_order_acquire);
        low = static_cast<uint16_t>(tim.CNT);
        high2 = overflow_cnt.load(std::memory_order_acquire);
    } while (high1 != high2);

    if ((tim.SR & (1U << 0)) && (low < 32768U)) {
        if ((tim.CR1 & (1U << 4)) == 0) {
            high1++;
        } else {
            high1--;
        }
    }
    return (static_cast<int64_t>(high1) << 16) | low;
}
