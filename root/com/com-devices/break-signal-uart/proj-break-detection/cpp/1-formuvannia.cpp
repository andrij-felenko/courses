// dmx_transmitter.hpp / .cpp - Генератор пакетів DMX512 на C++20
#include <cstdint>
#include <array>
#include <span>

extern "C" {
    void hw_delay_us(uint32_t us);
    void uart_tx_pin_set_gpio_low();
    void uart_tx_pin_set_gpio_high();
    void uart_tx_pin_restore_peripheral();
    void uart_send_byte_blocking(uint8_t byte);
}

class DmxTransmitter {
public:
    static constexpr size_t ChannelCount = 512;
    static constexpr uint32_t BreakDurationUs = 100; // >= 88 мкс
    static constexpr uint32_t MabDurationUs = 12;    // >= 8 мкс

    struct Packet {
        uint8_t start_code{0x00};
        std::array<uint8_t, ChannelCount> channels{};
    };

    void send_packet(const Packet& packet) const {
        // 1. Апаратний перехід у стан Break через GPIO
        uart_tx_pin_set_gpio_low();
        hw_delay_us(BreakDurationUs);

        // 2. Інтервал Mark After Break
        uart_tx_pin_set_gpio_high();
        hw_delay_us(MabDurationUs);

        // 3. Відновлення периферії UART
        uart_tx_pin_restore_peripheral();

        // 4. Стартовий код
        uart_send_byte_blocking(packet.start_code);

        // 5. Послідовна передача слотів даних через безпечний span
        std::span<const uint8_t> slots{packet.channels};
        for (uint8_t val : slots) {
            uart_send_byte_blocking(val);
        }
    }
};
