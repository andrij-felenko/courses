#include <cstdint>
#include <concepts>

#if defined(PLATFORM_ESP32)
    #include <Arduino.h>
#elif defined(PLATFORM_STM32)
    #include "stm32f4xx_hal.h"
#endif

// Концепт апаратного виводу для статичного поліморфізму без vtable
template <typename T>
concept DigitalOutput = requires(T dev, bool state) {
    { dev.write(state) } -> std::same_as<void>;
    { dev.toggle() } -> std::same_as<void>;
};

// Реалізація під ESP32 на базі Arduino API
class Esp32GpioPin {
public:
    explicit constexpr Esp32GpioPin(uint8_t pin, bool active_high = true) noexcept
        : pin_{pin}, active_high_{active_high} {}

    void init() noexcept {
        pinMode(pin_, OUTPUT);
        write(false);
    }

    void write(bool state) const noexcept {
        const bool level = (state == active_high_);
        digitalWrite(pin_, level ? HIGH : LOW);
    }

    void toggle() noexcept {
        current_state_ = !current_state_;
        write(current_state_);
    }

private:
    uint8_t pin_{0};
    bool active_high_{true};
    bool current_state_{false};
};

// Реалізація під STM32 на базі STM32Cube HAL
class Stm32GpioPin {
public:
    constexpr Stm32GpioPin(GPIO_TypeDef *port, uint16_t pin_mask, bool active_high = true) noexcept
        : port_{port}, pin_mask_{pin_mask}, active_high_{active_high} {}

    void init() noexcept {
        if (port_ == GPIOA) {
            __HAL_RCC_GPIOA_CLK_ENABLE();
        }
        GPIO_InitTypeDef gpio{};
        gpio.Pin = pin_mask_;
        gpio.Mode = GPIO_MODE_OUTPUT_PP;
        gpio.Pull = GPIO_NOPULL;
        gpio.Speed = GPIO_SPEED_FREQ_LOW;
        HAL_GPIO_Init(port_, &gpio);
        write(false);
    }

    void write(bool state) const noexcept {
        const bool level = (state == active_high_);
        HAL_GPIO_WritePin(port_, pin_mask_, level ? GPIO_PIN_SET : GPIO_PIN_RESET);
    }

    void toggle() const noexcept {
        HAL_GPIO_TogglePin(port_, pin_mask_);
    }

private:
    GPIO_TypeDef *port_{GPIOA};
    uint16_t pin_mask_{GPIO_PIN_5};
    bool active_high_{true};
};

// Загальний контролер індикації, що працює з будь-яким типом піна
template <DigitalOutput PinType>
class StatusIndicator {
public:
    explicit StatusIndicator(PinType pin) : pin_{pin} {
        pin_.init();
    }

    void report_ok() {
        pin_.write(true);
    }

    void report_fault() {
        pin_.toggle();
    }

private:
    PinType pin_;
};
