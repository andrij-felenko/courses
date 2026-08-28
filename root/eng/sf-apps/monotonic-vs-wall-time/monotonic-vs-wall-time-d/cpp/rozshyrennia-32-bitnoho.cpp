#include <cstdint>
#include <atomic>

class HighResClock64 {
public:
    static void on_timer_interrupt(uint32_t current_raw) noexcept {
        static uint32_t last_raw = 0;
        if (current_raw < last_raw) {
            s_high_epoch.fetch_add(1, std::memory_order_relaxed);
        }
        last_raw = current_raw;
    }

    static uint64_t now_ticks() noexcept {
        uint32_t high1, high2, low;
        do {
            high1 = s_high_epoch.load(std::memory_order_acquire);
            low   = get_hardware_counter_32();
            high2 = s_high_epoch.load(std::memory_order_acquire);
        } while (high1 != high2);

        return (static_cast<uint64_t>(high1) << 32) | low;
    }

private:
    static inline std::atomic<uint32_t> s_high_epoch{0};
    static uint32_t get_hardware_counter_32() noexcept;
};
