#ifndef I2C_BUS_RECOVERY_HPP
#define I2C_BUS_RECOVERY_HPP

#include <cstdint>
#include <chrono>
#include <expected>
#include "stm32f4xx.h"
#include "dwt_timeout.hpp"

enum class I2cRecoveryError : uint8_t {
    SclStuckLow,
    SdaStuckLow,
    InvalidHardware
};

struct GpioPinConfig {
    GPIO_TypeDef* port{nullptr};
    uint8_t pin{0};
    uint8_t af{4};

    void set_output_open_drain() const noexcept {
        port->BSRR = (1U << pin);
        port->MODER &= ~(3U << (pin * 2));
        port->MODER |= (1U << (pin * 2));
        port->OTYPER |= (1U << pin);
        port->OSPEEDR |= (3U << (pin * 2));
        port->PUPDR &= ~(3U << (pin * 2));
    }

    void set_alternate_function_open_drain() const noexcept {
        port->MODER &= ~(3U << (pin * 2));
        port->MODER |= (2U << (pin * 2));
        port->OTYPER |= (1U << pin);
        if (pin < 8) {
            port->AFR[0] &= ~(0xFU << (pin * 4));
            port->AFR[0] |= (static_cast<uint32_t>(af) << (pin * 4));
        } else {
            port->AFR[1] &= ~(0xFU << ((pin - 8) * 4));
            port->AFR[1] |= (static_cast<uint32_t>(af) << ((pin - 8) * 4));
        }
    }

    void set_high() const noexcept { port->BSRR = (1U << pin); }
    void set_low() const noexcept { port->BSRR = (1U << (pin + 16)); }
    [[nodiscard]] bool read() const noexcept { return (port->IDR & (1U << pin)) != 0; }
};

class I2cBusRecoveryEngine {
public:
    struct Hardware {
        I2C_TypeDef* i2c{nullptr};
        GpioPinConfig scl{};
        GpioPinConfig sda{};
    };

    struct RecoveryReport {
        uint8_t pulses_applied{0};
        bool sda_initially_stuck{false};
    };

    static std::expected<RecoveryReport, I2cRecoveryError> execute(const Hardware& hw) noexcept {
        if (!hw.i2c || !hw.scl.port || !hw.sda.port) {
            return std::unexpected(I2cRecoveryError::InvalidHardware);
        }

        RecoveryReport report{};

        // 1. Вимикаємо I2C
        hw.i2c->CR1 &= ~I2C_CR1_PE;

        // 2. Переводимо піни в GPIO Open-Drain
        hw.scl.set_output_open_drain();
        hw.sda.set_output_open_drain();

        DwtTimer::delay(std::chrono::microseconds{10});

        // 3. Перевірка SCL
        if (!hw.scl.read()) {
            hw.scl.set_alternate_function_open_drain();
            hw.sda.set_alternate_function_open_drain();
            return std::unexpected(I2cRecoveryError::SclStuckLow);
        }

        report.sda_initially_stuck = !hw.sda.read();

        // 4. Подача до 9 імпульсів
        bool freed = false;
        for (uint8_t i = 0; i < 9; ++i) {
            if (hw.sda.read()) {
                freed = true;
                break;
            }
            report.pulses_applied++;

            hw.scl.set_low();
            DwtTimer::delay(std::chrono::microseconds{5});
            hw.scl.set_high();
            DwtTimer::delay(std::chrono::microseconds{5});
        }

        if (hw.sda.read()) {
            freed = true;
        }

        // 5. Умова STOP
        hw.sda.set_low();
        DwtTimer::delay(std::chrono::microseconds{5});
        hw.scl.set_high();
        DwtTimer::delay(std::chrono::microseconds{5});
        hw.sda.set_high();
        DwtTimer::delay(std::chrono::microseconds{10});

        // 6. Відновлення режимів пінів
        hw.scl.set_alternate_function_open_drain();
        hw.sda.set_alternate_function_open_drain();

        // 7. Скидання модуля периферії
        hw.i2c->CR1 |= I2C_CR1_SWRST;
        DwtTimer::delay(std::chrono::microseconds{5});
        hw.i2c->CR1 &= ~I2C_CR1_SWRST;
        hw.i2c->CR1 |= I2C_CR1_PE;

        if (!freed) {
            return std::unexpected(I2cRecoveryError::SdaStuckLow);
        }

        return report;
    }
};

#endif // I2C_BUS_RECOVERY_HPP
