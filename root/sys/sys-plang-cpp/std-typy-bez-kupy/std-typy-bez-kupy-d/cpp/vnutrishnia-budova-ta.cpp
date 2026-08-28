#include <optional>
#include <cstdint>

struct UartHardware {
    static bool has_data() noexcept;
    static uint8_t read_rx_register() noexcept;
};

// Замість магічного int16_t з поверненням -1 при порожньому буфері
[[nodiscard]] std::optional<uint8_t> uart_try_read_byte() noexcept {
    if (!UartHardware::has_data()) {
        return std::nullopt; // Порожній стан, 0 копіювань
    }
    return UartHardware::read_rx_register();
}

void handle_uart() {
    auto byte_opt = uart_try_read_byte();
    if (byte_opt.has_value()) {
        uint8_t received = *byte_opt; // Безпечний доступ до значення
        (void)received;
    }

    // Отримання значення за замовчуванням у разі відсутності
    uint8_t data = byte_opt.value_or(0x00);
    (void)data;
}
