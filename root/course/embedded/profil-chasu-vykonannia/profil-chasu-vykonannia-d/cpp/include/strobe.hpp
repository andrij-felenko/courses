// Строб для осцилографа. Порт і пін — параметри шаблону, тому адреса
// регістра BSRR обчислюється під час компіляції, а в коді лишається
// єдиний STR: атомарна установка або скидання без читання регістра.
#pragma once

#include <cstdint>

#include "stm32f4xx.h"

namespace prof {

template <std::uintptr_t PortBase, unsigned Pin>
struct GpioStrobe {
    static_assert(Pin < 16U, "у порту STM32 шістнадцять виводів");

    static void configure() noexcept
    {
        auto* const port = reinterpret_cast<GPIO_TypeDef*>(PortBase);
        port->MODER = (port->MODER & ~(0b11U << (Pin * 2U))) | (0b01U << (Pin * 2U));
        port->OTYPER &= ~(1U << Pin);
        port->OSPEEDR |= (0b11U << (Pin * 2U));   // найкрутіший фронт
        low();
    }

    static void high() noexcept { bsrr() = (1U << Pin); }
    static void low() noexcept { bsrr() = (1U << (Pin + 16U)); }

private:
    static volatile std::uint32_t& bsrr() noexcept
    {
        return *reinterpret_cast<volatile std::uint32_t*>(PortBase + 0x18U);
    }
};

// RAII знімає єдину слабкість сишного строба: пін падає на будь-якому
// виході з області видимості, зокрема на ранньому return у гілці помилки.
template <class Pin>
class [[nodiscard]] ScopeStrobe {
public:
    ScopeStrobe() noexcept { Pin::high(); }
    ~ScopeStrobe() noexcept { Pin::low(); }

    ScopeStrobe(const ScopeStrobe&) = delete;
    ScopeStrobe& operator=(const ScopeStrobe&) = delete;
};

}  // namespace prof
