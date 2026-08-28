#include <cstdint>
#include <chrono>
#include <expected>
#include "stm32f4xx.h"

struct BusPin {
    GPIO_TypeDef* port;
    uint8_t pin;

    void set_high() const noexcept { port->BSRR = (1U << pin); }
    void set_low() const noexcept { port->BSRR = (1U << (pin + 16)); }
    [[nodiscard]] bool read() const noexcept { return (port->IDR & (1U << pin)) != 0; }

    void configure_open_drain() const noexcept {
        port->MODER &= ~(3U << (pin * 2));
        port->MODER |= (1U << (pin * 2)); // Output mode
        port->OTYPER |= (1U << pin);      // Open-drain
        port->OSPEEDR |= (3U << (pin * 2));
    }

    void configure_alternate_function() const noexcept {
        port->MODER &= ~(3U << (pin * 2));
        port->MODER |= (2U << (pin * 2)); // AF mode
    }
};

class I2cRecoveryEngine {
public:
    static std::expected<void, BusError> recover(BusPin scl, BusPin sda, I2C_TypeDef* i2c) noexcept {
        i2c->CR1 &= ~I2C_CR1_PE; // Вимикаємо периферію

        scl.set_high();
        sda.set_high();
        scl.configure_open_drain();
        sda.configure_open_drain();

        delay_us(10);

        // Перевірка стану лінії SCL
        if (!scl.read()) {
            return std::unexpected(BusError::BusStuck);
        }

        bool freed = false;
        for (int pulse = 0; pulse < 9; ++pulse) {
            if (sda.read()) {
                freed = true;
                break;
            }
            scl.set_low();
            delay_us(5);
            scl.set_high();
            delay_us(5);
        }

        if (sda.read()) {
            freed = true;
        }

        // Примусова умова STOP
        sda.set_low();
        delay_us(5);
        scl.set_high();
        delay_us(5);
        sda.set_high();
        delay_us(10);

        // Відновлення режимів пінів
        scl.configure_alternate_function();
        sda.configure_alternate_function();

        // Скидання модуля
        i2c->CR1 |= I2C_CR1_SWRST;
        delay_us(5);
        i2c->CR1 &= ~I2C_CR1_SWRST;
        i2c->CR1 |= I2C_CR1_PE;

        if (!freed) {
            return std::unexpected(BusError::BusStuck);
        }
        return {};
    }

private:
    static void delay_us(uint32_t us) noexcept {
        const uint32_t start = DWT->CYCCNT;
        const uint32_t ticks = static_cast<uint32_t>((static_cast<uint64_t>(us) * SystemCoreClock) / 1'000'000ULL);
        while ((DWT->CYCCNT - start) < ticks);
    }
};
