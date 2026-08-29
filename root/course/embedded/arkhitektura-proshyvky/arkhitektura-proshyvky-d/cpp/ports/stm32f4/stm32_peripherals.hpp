// ports/stm32f4/stm32_peripherals.hpp — внутрішній інтерфейс порту.
// Заголовок бачать лише файли самого порту: застосунок отримує плату
// через board.hpp і про існування цих класів не здогадується.
#pragma once

#include "app/telemetry.hpp"
#include "hal/gpio.hpp"
#include "hal/i2c_bus.hpp"

#include "stm32f4xx.h"

namespace port {

// Контролер I2C1 на виводах PB6 (SCL) і PB7 (SDA).
class Stm32I2cBus final : public hal::II2cBus {
public:
    explicit Stm32I2cBus(I2C_TypeDef* regs) noexcept : regs_{regs} {}

    void init();

    [[nodiscard]] std::expected<void, hal::I2cError>
    write(std::uint8_t address, std::span<const std::uint8_t> data) override;

    [[nodiscard]] std::expected<void, hal::I2cError>
    read(std::uint8_t address, std::span<std::uint8_t> data) override;

    [[nodiscard]] std::expected<void, hal::I2cError>
    write_read(std::uint8_t address,
               std::span<const std::uint8_t> tx,
               std::span<std::uint8_t> rx) override;

private:
    // Прийом без очікування вільної шини: під час повторного START вона
    // навмисно лишається зайнятою.
    [[nodiscard]] std::expected<void, hal::I2cError>
    receive(std::uint8_t address, std::span<std::uint8_t> data);

    [[nodiscard]] std::expected<void, hal::I2cError> wait_flag(std::uint32_t mask);
    [[nodiscard]] std::expected<void, hal::I2cError> wait_not_busy();
    [[nodiscard]] std::expected<void, hal::I2cError> start(std::uint8_t address, bool reading);
    void clear_addr();

    I2C_TypeDef* regs_;
};

class Stm32GpioPort final : public hal::IGpioPort {
public:
    explicit Stm32GpioPort(GPIO_TypeDef* regs) noexcept : regs_{regs} {}

    void configure(std::uint8_t pin, hal::PinMode mode) override;
    void set(std::uint8_t pin, bool level) override;
    [[nodiscard]] bool get(std::uint8_t pin) const override;

private:
    GPIO_TypeDef* regs_;
};

// Передавач телеметрії: USART2, 115200 бод, вивід PA2.
class UartTelemetrySink final : public app::ITelemetrySink {
public:
    void init();
    void publish(const app::TelemetryRecord& record) override;

private:
    static void put_char(char c);
    static void put_text(std::string_view text);
    static void put_uint(std::uint32_t value);
    static void put_fixed2(float value);
};

// Налаштовує зовнішнє переривання від кнопки на PA0.
void button_exti_init();

} // namespace port
