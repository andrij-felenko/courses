#include <cstdint>
#include <string_view>
#include <span>

/* Типобезпечна C++ обгортка над апаратним блоком UART */
struct UartHardware {
    volatile uint32_t SR;
    volatile uint32_t DR;
    volatile uint32_t BRR;
    volatile uint32_t CR1;

    static constexpr uint32_t TXE_FLAG = (1U << 7);

    void send_byte(uint8_t byte) noexcept {
        while (!(SR & TXE_FLAG)) {
            // Очікування готовності апаратного каскаду
        }
        DR = byte;
    }

    void write(std::string_view msg) noexcept {
        for (char ch : msg) {
            send_byte(static_cast<uint8_t>(ch));
        }
    }

    void write_bytes(std::span<const uint8_t> buffer) noexcept {
        for (uint8_t b : buffer) {
            send_byte(b);
        }
    }
};
