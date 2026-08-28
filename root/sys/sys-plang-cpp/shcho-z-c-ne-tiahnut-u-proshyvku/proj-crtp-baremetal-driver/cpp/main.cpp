#include <cstdint>
#include <cstddef>
#include <span>
#include <expected>
#include <concepts>

/* Типобезпечні коди помилок драйвера */
enum class DriverError : uint8_t {
    BufferOverflow,
    HardwareTimeout,
    Busy
};

/* Апаратні регістри мікроконтролера */
struct HardwareUartRegs {
    volatile uint32_t ISR;
    volatile uint32_t RDR;
    volatile uint32_t TDR;
};

inline constexpr uint32_t UART_ISR_TXE = (1U << 7);

/* Базовий протокольний клас CRTP (Static Polymorphism) */
template <typename Derived>
class PacketTransceiver {
public:
    /* Відправка пакета без використання винятків і динамічної пам'яті */
    [[nodiscard]] std::expected<size_t, DriverError> 
    transmit_packet(std::span<const uint8_t> payload) noexcept {
        if (payload.size() > 254) {
            return std::unexpected(DriverError::BufferOverflow);
        }

        /* Доступ до похідного класу через static_cast під час компіляції */
        auto& hw = static_cast<Derived&>(*this);

        /* 1. Заголовок кадру */
        if (auto res = hw.send_byte(0xAA); !res) {
            return std::unexpected(res.error());
        }

        /* 2. Довжина даних */
        if (auto res = hw.send_byte(static_cast<uint8_t>(payload.size())); !res) {
            return std::unexpected(res.error());
        }

        /* 3. Корисне навантаження */
        for (const uint8_t byte : payload) {
            if (auto res = hw.send_byte(byte); !res) {
                return std::unexpected(res.error());
            }
        }

        /* 4. Контрольна сума CRC-8 */
        const uint8_t crc = calculate_crc8(payload);
        if (auto res = hw.send_byte(crc); !res) {
            return std::unexpected(res.error());
        }

        return payload.size() + 3; /* Загальна кількість переданих байтів */
    }

protected:
    /* Захищений деструктор запобігає поліморфному видаленню */
    ~PacketTransceiver() = default;

private:
    [[nodiscard]] static constexpr uint8_t calculate_crc8(std::span<const uint8_t> data) noexcept {
        uint8_t crc = 0x00;
        for (const uint8_t b : data) {
            crc ^= b;
            for (uint8_t bit = 0; bit < 8; ++bit) {
                if (crc & 0x80) {
                    crc = static_cast<uint8_t>((crc << 1) ^ 0x07);
                } else {
                    crc = static_cast<uint8_t>(crc << 1);
                }
            }
        }
        return crc;
    }
};

/* Конкретний драйвер апаратного UART для STM32 */
class Stm32UartDriver : public PacketTransceiver<Stm32UartDriver> {
public:
    constexpr explicit Stm32UartDriver(HardwareUartRegs* regs, uint32_t timeout_cycles = 10000) noexcept
        : m_regs(regs), m_timeout(timeout_cycles) {}

    /* Прямий запис у периферійні регістри (компілятор інлайнить цей метод) */
    [[nodiscard]] std::expected<void, DriverError> send_byte(uint8_t byte) noexcept {
        uint32_t counter = m_timeout;
        while (!(m_regs->ISR & UART_ISR_TXE)) {
            if (--counter == 0) {
                return std::unexpected(DriverError::HardwareTimeout);
            }
        }
        m_regs->TDR = byte;
        return {};
    }

private:
    HardwareUartRegs* m_regs;
    uint32_t m_timeout;
};
