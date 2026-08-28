#include <cstdint>
#include <span>
#include <expected>

struct SpiRegisters {
    volatile uint32_t CR1;
    volatile uint32_t CR2;
    volatile uint32_t SR;
    volatile uint32_t DR;
    volatile uint32_t CRCPR;
    volatile uint32_t RXCRCR;
    volatile uint32_t TXCRCR;
    volatile uint32_t I2SCFGR;
};

enum class SpiError : uint8_t {
    Timeout,
    Overrun,
    ModeFault,
    BufferMismatch
};

class SpiBusController {
public:
    static constexpr uint32_t FlagRxne = 1U << 0;
    static constexpr uint32_t FlagTxe  = 1U << 1;
    static constexpr uint32_t FlagBsy  = 1U << 7;
    static constexpr uint32_t FlagOvr  = 1U << 6;
    static constexpr uint32_t FlagModf = 1U << 5;

    explicit constexpr SpiBusController(uintptr_t base_addr) noexcept
        : regs_(reinterpret_cast<SpiRegisters*>(base_addr)) {}

    [[nodiscard]] std::expected<uint8_t, SpiError> transfer_byte(uint8_t tx_data, uint32_t timeout_cycles = 100000) const noexcept {
        uint32_t timeout = timeout_cycles;

        // 1. Очікуємо готовності TX буфера
        while (!(regs_->SR & FlagTxe)) {
            if (--timeout == 0) return std::unexpected(SpiError::Timeout);
        }

        // 2. Старт передачі
        regs_->DR = tx_data;

        timeout = timeout_cycles;
        // 3. Очікуємо заповнення RX буфера
        while (!(regs_->SR & FlagRxne)) {
            if (regs_->SR & FlagOvr) {
                clear_overrun();
                return std::unexpected(SpiError::Overrun);
            }
            if (regs_->SR & FlagModf) {
                return std::unexpected(SpiError::ModeFault);
            }
            if (--timeout == 0) return std::unexpected(SpiError::Timeout);
        }

        return static_cast<uint8_t>(regs_->DR & 0xFF);
    }

    [[nodiscard]] std::expected<void, SpiError> transfer_buffer(
        std::span<const uint8_t> tx_buf,
        std::span<uint8_t> rx_buf,
        uint32_t timeout_cycles = 100000) const noexcept 
    {
        if (!rx_buf.empty() && rx_buf.size() != tx_buf.size()) {
            return std::unexpected(SpiError::BufferMismatch);
        }

        for (size_t i = 0; i < tx_buf.size(); ++i) {
            auto res = transfer_byte(tx_buf[i], timeout_cycles);
            if (!res) return std::unexpected(res.error());
            if (!rx_buf.empty()) {
                rx_buf[i] = *res;
            }
        }
        return {};
    }

private:
    SpiRegisters* const regs_;

    void clear_overrun() const noexcept {
        [[maybe_unused]] volatile uint32_t dummy_dr = regs_->DR;
        [[maybe_unused]] volatile uint32_t dummy_sr = regs_->SR;
    }
};
