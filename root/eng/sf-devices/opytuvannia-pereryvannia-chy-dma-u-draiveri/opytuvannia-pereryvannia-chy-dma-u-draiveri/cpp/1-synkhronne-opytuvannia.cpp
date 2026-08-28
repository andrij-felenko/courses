#include <cstdint>
#include <expected>

struct SimpleUart {
    volatile uint32_t SR;
    volatile uint32_t DR;
};

inline constexpr uint32_t UART_SR_TXE = (1u << 7);

enum class UartError { Timeout };

class SimplePollingUart {
public:
    [[nodiscard]] static std::expected<void, UartError> send_byte(SimpleUart* uart, uint8_t byte, uint32_t timeout_ticks) noexcept {
        auto* dwt_cyccnt = reinterpret_cast<volatile uint32_t*>(0xE0001004);
        const uint32_t start = *dwt_cyccnt;

        while (!(uart->SR & UART_SR_TXE)) {
            if ((*dwt_cyccnt - start) >= timeout_ticks) {
                return std::unexpected(UartError::Timeout);
            }
        }
        uart->DR = byte;
        return {};
    }
};
