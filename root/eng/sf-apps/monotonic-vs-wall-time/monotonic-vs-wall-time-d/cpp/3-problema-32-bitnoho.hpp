/* C++20 вбудований системний лічильник мілісекунд */
#include <cstdint>
#include <atomic>

class SystemTick {
public:
    static void isr_increment() noexcept {
        ticks_.fetch_add(1, std::memory_order_relaxed);
    }

    [[nodiscard]] static uint32_t get_tick() noexcept {
        return ticks_.load(std::memory_order_relaxed);
    }

private:
    static inline std::atomic<uint32_t> ticks_{0};
};
