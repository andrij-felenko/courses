// Ідіоматичне стробування GPIO на C++20 з використанням RAII
#pragma once
#include <cstdint>
#include <concepts>

namespace embedded::timing {

template <uintptr_t PortBase, uint8_t PinNumber>
struct GpioPinStrobe {
    static_assert(PinNumber < 16, "Pin index out of range (0..15)");

    static inline void high() noexcept {
        auto* const bsrr = reinterpret_cast<volatile uint32_t*>(PortBase + 0x18);
        *bsrr = (1UL << PinNumber);
    }

    static inline void low() noexcept {
        auto* const bsrr = reinterpret_cast<volatile uint32_t*>(PortBase + 0x18);
        *bsrr = (1UL << (PinNumber + 16));
    }
};

template <typename GpioPin>
class [[nodiscard]] ScopeStrobe {
public:
    inline ScopeStrobe() noexcept {
        GpioPin::high();
    }
    inline ~ScopeStrobe() noexcept {
        GpioPin::low();
    }

    ScopeStrobe(const ScopeStrobe&) = delete;
    ScopeStrobe& operator=(const ScopeStrobe&) = delete;
};

} // namespace embedded::timing

// Використання в коді:
using DebugStrobe = embedded::timing::GpioPinStrobe<0x40020400UL, 5>; // GPIOB Base, Pin 5

extern "C" void TIM2_IRQHandler() {
    {
        embedded::timing::ScopeStrobe<DebugStrobe> strobe;
        execute_control_loop_iteration();
    } // Пін автоматично скидається в 0 при виході з області видимості

    TIM2->SR = ~TIM_SR_UIF;
}
