#include <cstdint>
#include <cstddef>
#include <span>

namespace hardware {

/* Регістрова карта таймера загального призначення за Reference Manual */
struct TimerBlock {
    volatile uint32_t cr1;    // +0x00: Control Register 1
    volatile uint32_t cr2;    // +0x04: Control Register 2
    volatile uint32_t smcr;   // +0x08: Slave Mode Control
    volatile uint32_t dier;   // +0x0C: DMA/Interrupt Enable
    volatile uint32_t sr;     // +0x10: Status Register (W1C / rc_w0)
    volatile uint32_t egr;    // +0x14: Event Generation
    volatile uint32_t ccmr1;  // +0x18: Capture/Compare Mode 1
    volatile uint32_t ccmr2;  // +0x1C: Capture/Compare Mode 2
    volatile uint32_t ccer;   // +0x20: Capture/Compare Enable
    volatile uint32_t cnt;    // +0x24: Counter Register
    volatile uint32_t psc;    // +0x28: Prescaler Register
    volatile uint32_t arr;    // +0x2C: Auto-Reload Register
};

struct DbgBlock {
    volatile uint32_t idcode; // +0x00: Device ID & Revision
};

inline constexpr uintptr_t rcc_address    = 0x40023800UL;
inline constexpr uintptr_t tim2_address   = 0x40000000UL;
inline constexpr uintptr_t dbgmcu_address = 0xE0042000UL;

namespace timer_bits {
    inline constexpr uint32_t cr1_cen  = 1UL << 0;
    inline constexpr uint32_t dier_uie = 1UL << 0;
    inline constexpr uint32_t sr_uif   = 1UL << 0;
    inline constexpr uint32_t egr_ug   = 1UL << 0;
}

class PeriodicTimer {
public:
    explicit constexpr PeriodicTimer(uintptr_t base_addr = tim2_address) noexcept
        : timer_(*reinterpret_cast<TimerBlock*>(base_addr)),
          dbg_(*reinterpret_cast<DbgBlock*>(dbgmcu_address)) {}

    PeriodicTimer(const PeriodicTimer&) = delete;
    PeriodicTimer& operator=(const PeriodicTimer&) = delete;

    [[nodiscard]] bool is_silicon_rev_a() const noexcept {
        return ((dbg_.idcode >> 16) & 0xFFFFU) == 0x1000U;
    }

    void init_1khz(uint32_t timer_clock_hz) noexcept {
        // 1. Увімкнення тактування шини APB1
        auto& rcc_apb1enr = *reinterpret_cast<volatile uint32_t*>(rcc_address + 0x40UL);
        rcc_apb1enr |= (1UL << 0); // TIM2EN

        // 2. Зупинка лічильника перед зміною конфігурації
        timer_.cr1 = 0;
        timer_.psc = (timer_clock_hz / 1'000'000UL) - 1UL;
        timer_.arr = 1'000UL - 1UL;

        // 3. Обхід апаратного дефекту для ревізії Rev A
        if (is_silicon_rev_a()) {
            timer_.egr = timer_bits::egr_ug;
            timer_.sr = 0;
        }

        // 4. Дозвіл переривання за переповненням
        timer_.dier |= timer_bits::dier_uie;

        // 5. Старт лічильника
        timer_.cr1 |= timer_bits::cr1_cen;
    }

    void handle_interrupt() noexcept {
        if ((timer_.sr & timer_bits::sr_uif) != 0) {
            // W1C скидання прапорця
            timer_.sr = ~timer_bits::sr_uif;
            asm volatile("dsb" ::: "memory");
        }
    }

private:
    TimerBlock& timer_;
    DbgBlock& dbg_;
};

} // namespace hardware
