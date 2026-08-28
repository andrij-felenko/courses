#include <cstdint>

// Типова помилка у C++: спроба мапування сирого вказівника без volatile
inline std::uint32_t* const uart_status = reinterpret_cast<std::uint32_t*>(0x40013800);
inline std::uint32_t* const uart_data   = reinterpret_cast<std::uint32_t*>(0x40013804);
constexpr std::uint32_t usart_sr_txe = (1U << 7);

void uart_send_byte(std::uint8_t byte) {
    while (!(*uart_status & usart_sr_txe)) {
        // Очікування прапорця
    }
    *uart_data = byte;
}
