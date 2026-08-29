// ports/host_mock/host_mocks.hpp — плата, якої немає.
// Той самий застосунок і ті самі драйвери, але замість шини I2C —
// імітація мікросхем у пам'яті, а замість SysTick — віртуальний годинник,
// що стрибає вперед миттєво. Прошивка проживає добу за частку секунди,
// і саме це робить збірку на кожен коміт можливою.
#pragma once

#include "app/telemetry.hpp"
#include "hal/gpio.hpp"
#include "hal/i2c_bus.hpp"

#include <array>
#include <cstdint>

namespace port {

// Мікросхема як карта регістрів плюс правила відповіді.
class MockDevice {
public:
    MockDevice(std::uint8_t address) noexcept : address_{address} {}

    [[nodiscard]] std::uint8_t address() const noexcept { return address_; }

    void set_reg(std::uint8_t reg, std::uint8_t value) noexcept { regs_[reg] = value; }
    void set_reg16(std::uint8_t reg, std::uint16_t value) noexcept;
    [[nodiscard]] std::uint8_t reg(std::uint8_t index) const noexcept { return regs_[index]; }

    void set_present(bool present) noexcept { present_ = present; }
    [[nodiscard]] bool present() const noexcept { return present_; }

    // Наступні count звертань зазнають невдачі із заданою помилкою. Так
    // перевіряють гілки обробки збоїв, які на живій платі не замовиш:
    // обрив шлейфа посеред читання не влаштуєш на вимогу.
    void inject_error(hal::I2cError error, unsigned count) noexcept;
    [[nodiscard]] bool take_injected(hal::I2cError& out) noexcept;

    void select(std::uint8_t reg) noexcept { pointer_ = reg; }
    [[nodiscard]] std::uint8_t read_next() noexcept;
    virtual void write_reg(std::uint8_t reg, std::uint8_t value);

    [[nodiscard]] std::uint8_t pointer() const noexcept { return pointer_; }

    virtual ~MockDevice() = default;

protected:
    std::array<std::uint8_t, 256> regs_{};

private:
    std::uint8_t  address_;
    std::uint8_t  pointer_{0};
    bool          present_{true};
    hal::I2cError inject_error_{hal::I2cError::Nack};
    unsigned      inject_left_{0};
};

// Імітація BME280: справжні калібрувальні коефіцієнти й режим forced.
class MockBme280 final : public MockDevice {
public:
    MockBme280();

    // Сирі коди АЦП. Значення за замовчуванням дають близько 25 °C.
    void set_raw(std::uint32_t adc_t, std::uint32_t adc_p, std::uint16_t adc_h);

    void write_reg(std::uint8_t reg, std::uint8_t value) override;
};

class MockAdxl345 final : public MockDevice {
public:
    MockAdxl345();

    void set_axes(std::int16_t x, std::int16_t y, std::int16_t z);
};

class MockI2cBus final : public hal::II2cBus {
public:
    MockI2cBus(MockBme280& environment, MockAdxl345& accelerometer) noexcept
        : env_{environment}, accel_{accelerometer} {}

    [[nodiscard]] std::expected<void, hal::I2cError>
    write(std::uint8_t address, std::span<const std::uint8_t> data) override;

    [[nodiscard]] std::expected<void, hal::I2cError>
    read(std::uint8_t address, std::span<std::uint8_t> data) override;

    // Скільки транзакцій пройшло шиною: дешева перевірка того, що драйвер
    // не опитує давач частіше, ніж обіцяв.
    [[nodiscard]] unsigned transactions() const noexcept { return transactions_; }

private:
    [[nodiscard]] std::expected<MockDevice*, hal::I2cError> select(std::uint8_t address);

    MockBme280& env_;
    MockAdxl345& accel_;
    unsigned    transactions_{0};
};

// Замість регістра BSRR — слово в пам'яті плюс лічильник перемикань.
// Тест питає «скільки разів блимнув світлодіод» і відрізняє штатний
// режим від аварійного, не маючи ані плати, ані ока.
class MockGpioPort final : public hal::IGpioPort {
public:
    void configure(std::uint8_t pin, hal::PinMode mode) override;
    void set(std::uint8_t pin, bool level) override;
    [[nodiscard]] bool get(std::uint8_t pin) const override;

    [[nodiscard]] unsigned toggles(std::uint8_t pin) const;

private:
    static constexpr std::size_t kPins = 16;

    std::array<bool, kPins>         level_{};
    std::array<unsigned, kPins>     toggles_{};
    std::array<hal::PinMode, kPins> mode_{};
};

// Друкує запис у консоль і рахує, скільки їх було.
class ConsoleTelemetrySink final : public app::ITelemetrySink {
public:
    void publish(const app::TelemetryRecord& record) override;

    [[nodiscard]] unsigned count() const noexcept { return count_; }

private:
    unsigned count_{0};
};

// Кладе подію натиску так само, як це зробив би обробник EXTI0.
void mock_button_click();

} // namespace port
