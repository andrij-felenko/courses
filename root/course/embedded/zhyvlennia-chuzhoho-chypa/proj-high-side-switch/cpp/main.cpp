#include <cstdint>
#include <chrono>
#include <expected>
#include <span>

/* Абстракція апаратного інтерфейсу GPIO */
namespace hal {
    enum class PinMode { Output, InputFloating, Peripheral };

    void set_pin_mode(uint32_t pin, PinMode mode) noexcept;
    void write_pin(uint32_t pin, bool state) noexcept;
    void delay(std::chrono::milliseconds ms) noexcept;
    bool i2c_probe(uint8_t address) noexcept;
}

enum class PowerDomainError {
    DeviceNotResponding,
    InvalidConfiguration
};

struct PowerDomainPins {
    uint32_t pwr_en;
    uint32_t sda;
    uint32_t scl;
    uint8_t  device_addr;
};

class PeripheralPowerDomain {
public:
    constexpr PeripheralPowerDomain(PowerDomainPins pins,
                                    std::chrono::milliseconds startup_delay = std::chrono::milliseconds(15),
                                    std::chrono::milliseconds discharge_delay = std::chrono::milliseconds(30)) noexcept
        : pins_(pins), startup_delay_(startup_delay), discharge_delay_(discharge_delay), is_powered_(false) {}

    ~PeripheralPowerDomain() noexcept {
        if (is_powered_) {
            power_off();
        }
    }

    /* Заборона небезпечного копіювання керування доменом */
    PeripheralPowerDomain(const PeripheralPowerDomain&) = delete;
    PeripheralPowerDomain& operator=(const PeripheralPowerDomain&) = delete;

    PeripheralPowerDomain(PeripheralPowerDomain&& other) noexcept
        : pins_(other.pins_), startup_delay_(other.startup_delay_),
          discharge_delay_(other.discharge_delay_), is_powered_(other.is_powered_) {
        other.is_powered_ = false;
    }

    void init() const noexcept {
        hal::set_pin_mode(pins_.pwr_en, hal::PinMode::Output);
        hal::write_pin(pins_.pwr_en, false);
        isolate_bus();
    }

    [[nodiscard]] std::expected<void, PowerDomainError> power_on() noexcept {
        /* Крок 1: Замикаємо P-MOSFET ключ */
        hal::write_pin(pins_.pwr_en, true);

        /* Крок 2: Очікуємо стабілізації напруги і завершення POR */
        hal::delay(startup_delay_);

        /* Крок 3: Підключаємо цифрові інтерфейси МК */
        hal::set_pin_mode(pins_.sda, hal::PinMode::Peripheral);
        hal::set_pin_mode(pins_.scl, hal::PinMode::Peripheral);

        /* Крок 4: Верифікація зв'язку */
        if (!hal::i2c_probe(pins_.device_addr)) {
            power_off();
            return std::unexpected(PowerDomainError::DeviceNotResponding);
        }

        is_powered_ = true;
        return {};
    }

    void power_off() noexcept {
        /* Крок 1: Ізоляція сигнальних ліній для усунення фантомного живлення */
        isolate_bus();

        /* Крок 2: Розмикання силового ключа */
        hal::write_pin(pins_.pwr_en, false);
        is_powered_ = false;

        /* Крок 3: Пауза на повний розряд вихідної ємності через R_dis */
        hal::delay(discharge_delay_);
    }

    [[nodiscard]] bool is_active() const noexcept {
        return is_powered_;
    }

private:
    void isolate_bus() const noexcept {
        hal::set_pin_mode(pins_.sda, hal::PinMode::InputFloating);
        hal::set_pin_mode(pins_.scl, hal::PinMode::InputFloating);
    }

    PowerDomainPins pins_;
    std::chrono::milliseconds startup_delay_;
    std::chrono::milliseconds discharge_delay_;
    bool is_powered_;
};

/* RAII-обгортка для сесійного опитування давача з гарантованим вимкненням */
class ScopedPowerSession {
public:
    explicit ScopedPowerSession(PeripheralPowerDomain& domain)
        : domain_(domain), status_(domain_.power_on()) {}

    ~ScopedPowerSession() noexcept {
        if (status_.has_value()) {
            domain_.power_off();
        }
    }

    [[nodiscard]] bool is_valid() const noexcept {
        return status_.has_value();
    }

    [[nodiscard]] PowerDomainError error() const noexcept {
        return status_.error();
    }

private:
    PeripheralPowerDomain& domain_;
    std::expected<void, PowerDomainError> status_;
};
