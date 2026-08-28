#include <cstdint>
#include <concepts>
#include <expected>
#include <span>

namespace embedded::bus {

enum class RecoveryStatus : uint8_t {
    Success,
    AlreadyFree
};

enum class RecoveryError : uint8_t {
    SclStuckLow,
    SdaStuckLow,
    HardwareFault
};

enum class PinLevel : bool {
    Low = false,
    High = true
};

// Концепт, що висуває вимоги до платформозалежного шару керування GPIO
template <typename T>
concept GpioDriver = requires(T drv, uint32_t pin, PinLevel level) {
    { drv.set_open_drain(pin) } -> std::same_as<void>;
    { drv.set_alternate_i2c(pin) } -> std::same_as<void>;
    { drv.write(pin, level) } -> std::same_as<void>;
    { drv.read(pin) } -> std::same_as<PinLevel>;
    { drv.delay_us(10u) } -> std::same_as<void>;
};

template <GpioDriver Platform>
class I2cBusRecovery {
public:
    constexpr I2cBusRecovery(Platform& platform, uint32_t scl_pin, uint32_t sda_pin) noexcept
        : m_platform{platform}, m_scl{scl_pin}, m_sda{sda_pin} {}

    // Виконання процедури відновлення шини методом 9 тактів SCL
    [[nodiscard]] std::expected<RecoveryStatus, RecoveryError> recover() noexcept {
        // RAII-вартовий: гарантує повернення пінів у режим I2C при будь-якому виході з методу
        struct PinRestorer {
            Platform& plat;
            uint32_t scl;
            uint32_t sda;
            ~PinRestorer() noexcept {
                plat.set_alternate_i2c(scl);
                plat.set_alternate_i2c(sda);
            }
        } restorer{m_platform, m_scl, m_sda};

        m_platform.set_open_drain(m_scl);
        m_platform.set_open_drain(m_sda);
        m_platform.write(m_scl, PinLevel::High);
        m_platform.write(m_sda, PinLevel::High);
        m_platform.delay_us(10);

        // Перевірка SCL на замикання
        if (m_platform.read(m_scl) == PinLevel::Low) {
            return std::unexpected(RecoveryError::SclStuckLow);
        }

        // Перевірка, чи не вільна шина вже зараз
        if (m_platform.read(m_sda) == PinLevel::High) {
            return RecoveryStatus::AlreadyFree;
        }

        // Генерація до 9 імпульсів тактування
        bool sda_released = false;
        for (uint8_t i = 0; i < 9; ++i) {
            m_platform.write(m_scl, PinLevel::Low);
            m_platform.delay_us(5);

            m_platform.write(m_scl, PinLevel::High);
            m_platform.delay_us(5);

            if (m_platform.read(m_sda) == PinLevel::High) {
                sda_released = true;
                break;
            }
        }

        if (!sda_released) {
            return std::unexpected(RecoveryError::SdaStuckLow);
        }

        // Генерація умови STOP
        m_platform.write(m_scl, PinLevel::Low);
        m_platform.delay_us(5);
        m_platform.write(m_sda, PinLevel::Low);
        m_platform.delay_us(5);

        m_platform.write(m_scl, PinLevel::High);
        m_platform.delay_us(5);
        m_platform.write(m_sda, PinLevel::High);
        m_platform.delay_us(10);

        return RecoveryStatus::Success;
    }

private:
    Platform& m_platform;
    uint32_t m_scl;
    uint32_t m_sda;
};

} // namespace embedded::bus
