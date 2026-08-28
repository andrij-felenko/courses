#include <cstdint>
#include <cstddef>
#include <span>
#include <expected>

struct UartHardware {
    volatile uint32_t SR;
    volatile uint32_t DR;
    volatile uint32_t BRR;
    volatile uint32_t CR1;
};

inline constexpr uint32_t UART_SR_TXE  = (1u << 7);
inline constexpr uint32_t UART_SR_RXNE = (1u << 5);
inline constexpr uint32_t UART_SR_ORE  = (1u << 3);

enum class DriverError : int32_t {
    Timeout = -1,
    HardwareError = -2,
    InvalidParameter = -3
};

class PollingUartDriver {
private:
    UartHardware* hw_;

    [[nodiscard]] static uint32_t get_cycle_count() noexcept {
        auto* dwt_cyccnt = reinterpret_cast<volatile uint32_t*>(0xE0001004);
        return *dwt_cyccnt;
    }

public:
    explicit constexpr PollingUartDriver(UartHardware* hw) noexcept : hw_(hw) {}

    static void init_cycle_counter() noexcept {
        auto* demcr = reinterpret_cast<volatile uint32_t*>(0xE000EDFC);
        auto* dwt_ctrl = reinterpret_cast<volatile uint32_t*>(0xE0001000);
        *demcr |= (1u << 24);
        *dwt_ctrl |= (1u << 0);
    }

    [[nodiscard]] std::expected<size_t, DriverError> write(std::span<const uint8_t> buffer, uint32_t timeout_cycles) noexcept {
        if (!hw_) return std::unexpected(DriverError::InvalidParameter);

        size_t bytes_written = 0;
        for (const uint8_t byte : buffer) {
            const uint32_t start = get_cycle_count();
            while (!(hw_->SR & UART_SR_TXE)) {
                if ((get_cycle_count() - start) >= timeout_cycles) {
                    return std::unexpected(DriverError::Timeout);
                }
            }
            hw_->DR = byte;
            ++bytes_written;
        }
        return bytes_written;
    }

    [[nodiscard]] std::expected<size_t, DriverError> read(std::span<uint8_t> buffer, uint32_t timeout_cycles) noexcept {
        if (!hw_) return std::unexpected(DriverError::InvalidParameter);

        size_t bytes_read = 0;
        for (uint8_t& byte : buffer) {
            const uint32_t start = get_cycle_count();
            while (!(hw_->SR & UART_SR_RXNE)) {
                if (hw_->SR & UART_SR_ORE) {
                    [[maybe_unused]] volatile uint32_t dummy_sr = hw_->SR;
                    [[maybe_unused]] volatile uint32_t dummy_dr = hw_->DR;
                    return std::unexpected(DriverError::HardwareError);
                }
                if ((get_cycle_count() - start) >= timeout_cycles) {
                    return std::unexpected(DriverError::Timeout);
                }
            }
            byte = static_cast<uint8_t>(hw_->DR & 0xFF);
            ++bytes_read;
        }
        return bytes_read;
    }
};
