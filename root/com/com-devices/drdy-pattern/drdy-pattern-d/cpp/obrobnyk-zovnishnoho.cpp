#include <cstdint>
#include <atomic>

struct ExtiRegisters {
    volatile uint32_t pending;
    volatile uint32_t mask;
};

inline auto* const exti = reinterpret_cast<ExtiRegisters*>(0x40010400);
constexpr uint32_t drdy_line_mask = 1U << 4;

class SensorInterruptHandler {
public:
    static void handle_isr() noexcept {
        if (exti->pending & drdy_line_mask) {
            exti->pending = drdy_line_mask; // Скидання прапорця переривання
            
            data_ready_flag_.store(true, std::memory_order_release);
            event_counter_.fetch_add(1, std::memory_order_relaxed);
        }
    }

    static bool is_data_ready() noexcept {
        return data_ready_flag_.exchange(false, std::memory_order_acquire);
    }

    static uint32_t event_count() noexcept {
        return event_counter_.load(std::memory_order_relaxed);
    }

private:
    static inline std::atomic<bool> data_ready_flag_{false};
    static inline std::atomic<uint32_t> event_counter_{0};
};

extern "C" void EXTI4_IRQHandler() {
    SensorInterruptHandler::handle_isr();
}
