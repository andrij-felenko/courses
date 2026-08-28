#include <cstdint>
#include <atomic>

namespace mcu::debug {

struct DwtUnit {
    volatile uint32_t CTRL;
    volatile uint32_t CYCCNT;
    volatile uint32_t CPICNT;
    volatile uint32_t EXCCNT;
    volatile uint32_t SLEEPCNT;
    volatile uint32_t LSUCNT;
    volatile uint32_t FOLDCNT;
    volatile uint32_t PCSR;
};

inline auto& core_debug_demcr = *reinterpret_cast<volatile uint32_t*>(0xE000EDFCU);
inline auto& dwt = *reinterpret_cast<DwtUnit*>(0xE0001000U);
inline auto& nvic_ispr0 = *reinterpret_cast<volatile uint32_t*>(0xE000E200U);
inline auto& nvic_iser0 = *reinterpret_cast<volatile uint32_t*>(0xE000E100U);

class CycleProfiler {
public:
    static void enable() noexcept {
        /* Дозвіл трасування (TRCENA) */
        core_debug_demcr |= (1U << 24);
        dwt.CYCCNT = 0;
        dwt.CTRL |= (1U << 0);
        nvic_iser0 = (1U << 6);

        /* Визначення базової затримки читання регістра */
        const uint32_t t1 = dwt.CYCCNT;
        const uint32_t t2 = dwt.CYCCNT;
        overhead_ = t2 - t1;
    }

    [[nodiscard, gnu::always_inline]] static inline uint32_t now() noexcept {
        return dwt.CYCCNT;
    }

    [[nodiscard]] static inline uint32_t overhead() noexcept {
        return overhead_;
    }

    static inline void trigger_irq(uint8_t irq_num) noexcept {
        nvic_ispr0 = (1U << irq_num);
        asm volatile("dsb 0xF" ::: "memory");
        asm volatile("isb 0xF" ::: "memory");
    }

private:
    static inline uint32_t overhead_{0};
};

/* Збереження результатів профілювання */
struct LatencyReport {
    uint32_t start_cycles{0};
    uint32_t isr_entry_cycles{0};
    uint32_t total_latency{0};
};

inline LatencyReport global_report{};

} // namespace mcu::debug

extern "C" void EXTI0_IRQHandler_DWT_Cpp() {
    const uint32_t entry = mcu::debug::CycleProfiler::now();
    mcu::debug::global_report.isr_entry_cycles = entry;
    mcu::debug::global_report.total_latency = (entry - mcu::debug::global_report.start_cycles) 
                                            - mcu::debug::CycleProfiler::overhead();
}
