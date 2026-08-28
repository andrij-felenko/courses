// Налаштування апаратного Modbus RTO таймера (C++)
#include <cstdint>

struct HardwareReceiverTimeout {
    static constexpr void enable(std::uint32_t bit_clocks = 35) noexcept {
        USART1->RTOR = (bit_clocks & USART_RTOR_RTO_Msk);
        USART1->CR2 |= USART_CR2_RTOEN;
        USART1->CR1 |= USART_CR1_RTOIE;
    }
};
