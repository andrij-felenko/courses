#include <cstdint>

inline volatile uint32_t& UART_SR_REF = *reinterpret_cast<volatile uint32_t*>(0x40013800UL);
inline volatile uint32_t& UART_DR_REF = *reinterpret_cast<volatile uint32_t*>(0x40013804UL);
inline constexpr uint32_t RXNE_FLAG   = 1U << 5;

uint8_t uart_receive_byte_direct() noexcept {
    while (!(UART_SR_REF & RXNE_FLAG)) {
        // Очікування прапорця
    }
    return static_cast<uint8_t>(UART_DR_REF & 0xFFU);
}
