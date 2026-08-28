#include <cstdint>
#include <cstddef>
#include <span>
#include <expected>
#include <mutex>
#include <concepts>

namespace embedded::drivers {

enum class SpiClockMode : uint8_t {
    Mode0 = 0, // CPOL = 0, CPHA = 0 (Idle LOW, Sample Rising)
    Mode1 = 1, // CPOL = 0, CPHA = 1 (Idle LOW, Sample Falling)
    Mode2 = 2, // CPOL = 1, CPHA = 0 (Idle HIGH, Sample Falling)
    Mode3 = 3  // CPOL = 1, CPHA = 1 (Idle HIGH, Sample Rising)
};

enum class SpiBitOrder : uint8_t {
    MsbFirst = 0,
    LsbFirst = 1
};

enum class SpiError : uint8_t {
    InvalidArguments,
    ModeFault,
    Timeout,
    BusBusy
};

struct SpiSlaveConfig {
    uint32_t         baudrateHz;
    SpiClockMode     clockMode;
    SpiBitOrder      bitOrder;
    uint8_t          csPortId;
    uint8_t          csPinNum;
    uint16_t         leadDelayUs{2};   // t_lead
    uint16_t         lagDelayUs{2};    // t_lag
    uint16_t         settleDelayUs{2}; // t_settle
};

// RAII охоронець виводу Chip Select
template <typename GpioDriver>
class ChipSelectGuard {
public:
    ChipSelectGuard(GpioDriver& gpio, uint8_t port, uint8_t pin, uint16_t leadUs, uint16_t lagUs) noexcept
        : m_gpio{gpio}, m_port{port}, m_pin{pin}, m_lagUs{lagUs}
    {
        m_gpio.writePin(m_port, m_pin, false); // Активація CS (LOW)
        if (leadUs > 0) {
            m_gpio.delayUs(leadUs);
        }
    }

    ~ChipSelectGuard() noexcept {
        if (m_lagUs > 0) {
            m_gpio.delayUs(m_lagUs);
        }
        m_gpio.writePin(m_port, m_pin, true);  // Деактивація CS (HIGH)
    }

    ChipSelectGuard(const ChipSelectGuard&) = delete;
    ChipSelectGuard& operator=(const ChipSelectGuard&) = delete;

private:
    GpioDriver& m_gpio;
    uint8_t     m_port;
    uint8_t     m_pin;
    uint16_t    m_lagUs;
};

// Транзакційний менеджер шини SPI
template <typename SpiRegisters, typename GpioDriver, typename MutexType>
class SpiBusManager {
public:
    constexpr SpiBusManager(
        SpiRegisters& registers,
        GpioDriver&   gpio,
        MutexType&    mutex,
        uint32_t      busClockHz) noexcept
        : m_regs{registers}, m_gpio{gpio}, m_mutex{mutex}, m_busClockHz{busClockHz} {}

    [[nodiscard]] std::expected<void, SpiError> transfer(
        const SpiSlaveConfig& cfg,
        std::span<const uint8_t> txBuffer,
        std::span<uint8_t> rxBuffer) noexcept
    {
        const size_t len = txBuffer.empty() ? rxBuffer.size() : txBuffer.size();
        if (len == 0) {
            return std::unexpected(SpiError::InvalidArguments);
        }

        // Захоплення м'ютекса через RAII
        std::lock_guard<MutexType> lock(m_mutex);

        // Динамічна реконфігурація регістрів
        if (auto res = reconfigure(cfg); !res) {
            return std::unexpected(res.error());
        }

        // Керування виводом CS через RAII охоронець
        ChipSelectGuard<GpioDriver> csGuard(
            m_gpio, cfg.csPortId, cfg.csPinNum, cfg.leadDelayUs, cfg.lagDelayUs);

        // Повнодуплексний обмін даними
        for (size_t i = 0; i < len; ++i) {
            if (m_regs.SR & SpiRegisters::SR_MODF) {
                return std::unexpected(SpiError::ModeFault);
            }

            // Очікування готовності передавача (TXE)
            if (!waitForFlag(SpiRegisters::SR_TXE, true)) {
                return std::unexpected(SpiError::Timeout);
            }

            const uint8_t outByte = txBuffer.empty() ? 0xFF : txBuffer[i];
            m_regs.DR = outByte;

            // Очікування готовності приймача (RXNE)
            if (!waitForFlag(SpiRegisters::SR_RXNE, true)) {
                return std::unexpected(SpiError::Timeout);
            }

            const uint8_t inByte = static_cast<uint8_t>(m_regs.DR);
            if (!rxBuffer.empty()) {
                rxBuffer[i] = inByte;
            }
        }

        // Очікування повного спустошення зсувного регістра (BSY = 0)
        if (!waitForFlag(SpiRegisters::SR_BSY, false)) {
            return std::unexpected(SpiError::Timeout);
        }

        return {};
    }

private:
    [[nodiscard]] std::expected<void, SpiError> reconfigure(const SpiSlaveConfig& cfg) noexcept {
        // Перевірка прапорця Mode Fault
        if (m_regs.SR & SpiRegisters::SR_MODF) {
            [[maybe_unused]] volatile uint32_t dummy = m_regs.SR;
            m_regs.CR1 |= SpiRegisters::CR1_MSTR;
            return std::unexpected(SpiError::ModeFault);
        }

        if (!waitForFlag(SpiRegisters::SR_BSY, false)) {
            return std::unexpected(SpiError::Timeout);
        }

        // Вимкнення SPI перед зміною керуючих бітів
        m_regs.CR1 &= ~SpiRegisters::CR1_SPE;

        uint32_t cr1 = m_regs.CR1;
        cr1 &= ~(SpiRegisters::CR1_CPOL | SpiRegisters::CR1_CPHA | 
                 SpiRegisters::CR1_LSBFIRST | SpiRegisters::CR1_BR_MASK);

        if (cfg.clockMode == SpiClockMode::Mode2 || cfg.clockMode == SpiClockMode::Mode3) {
            cr1 |= SpiRegisters::CR1_CPOL;
        }
        if (cfg.clockMode == SpiClockMode::Mode1 || cfg.clockMode == SpiClockMode::Mode3) {
            cr1 |= SpiRegisters::CR1_CPHA;
        }

        if (cfg.bitOrder == SpiBitOrder::LsbFirst) {
            cr1 |= SpiRegisters::CR1_LSBFIRST;
        }

        cr1 |= calculatePrescaler(cfg.baudrateHz);
        cr1 |= SpiRegisters::CR1_MSTR;

        m_regs.CR1 = cr1;
        m_regs.CR1 |= SpiRegisters::CR1_SPE;

        if (cfg.settleDelayUs > 0) {
            m_gpio.delayUs(cfg.settleDelayUs);
        }

        return {};
    }

    [[nodiscard]] uint32_t calculatePrescaler(uint32_t targetBaud) const noexcept {
        const uint32_t div = m_busClockHz / targetBaud;
        if (div <= 2)   return (0u << 3);
        if (div <= 4)   return (1u << 3);
        if (div <= 8)   return (2u << 3);
        if (div <= 16)  return (3u << 3);
        if (div <= 32)  return (4u << 3);
        if (div <= 64)  return (5u << 3);
        if (div <= 128) return (6u << 3);
        return (7u << 3);
    }

    [[nodiscard]] bool waitForFlag(uint32_t mask, bool expectedSet) const noexcept {
        uint32_t timeout = 100000;
        while (--timeout > 0) {
            const bool isSet = (m_regs.SR & mask) != 0;
            if (isSet == expectedSet) {
                return true;
            }
        }
        return false;
    }

    SpiRegisters& m_regs;
    GpioDriver&   m_gpio;
    MutexType&    m_mutex;
    uint32_t      m_busClockHz;
};

} // namespace embedded::drivers
