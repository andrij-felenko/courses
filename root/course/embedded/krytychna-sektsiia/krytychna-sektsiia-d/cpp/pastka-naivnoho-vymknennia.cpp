#include <cstdint>
#include <span>

struct UartHardware {
    volatile std::uint32_t DR;
};
inline auto* const UART1 = reinterpret_cast<UartHardware*>(0x40013800UL);

// Допоміжна функція драйвера UART (низький рівень)
void uart_send_byte(std::uint8_t byte) noexcept {
    __disable_irq();
    UART1->DR = byte;
    __enable_irq(); // ПОМИЛКА: безумовне увімкнення переривань!
}

// Високорівнева функція відправки цілого пакету
void telemetry_send_packet(std::span<const std::uint8_t> payload) noexcept {
    __disable_irq(); // Зовнішня критична секція
    
    if (!payload.empty()) {
        uart_send_byte(payload[0]); // Вкладений виклик ламає захист
        
        // Переривання вже УВІМКНЕНІ! Код нижче незахищений.
        for (std::size_t i = 1; i < payload.size(); ++i) {
            UART1->DR = payload[i];
        }
    }
    
    __enable_irq();
}
