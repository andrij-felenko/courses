// Конфігурація апаратного DE (RS-485 Driver Enable, C++)
#include <cstdint>

struct HardwareDriverEnable {
    static constexpr void configure(std::uint8_t assert_clocks = 4, std::uint8_t deassert_clocks = 4) noexcept {
        USART1->CR3 |= USART_CR3_DEM;
        USART1->CR3 &= ~USART_CR3_DEP;
        USART1->CR3 |= (static_cast<std::uint32_t>(assert_clocks) << USART_CR3_DEAT_Pos);
        USART1->CR3 |= (static_cast<std::uint32_t>(deassert_clocks) << USART_CR3_DEDT_Pos);
    }
};
