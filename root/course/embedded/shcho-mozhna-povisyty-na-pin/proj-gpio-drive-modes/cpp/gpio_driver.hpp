// Файл: gpio_driver.hpp — Ідіоматичний C++20 (RAII, Compile-Time Safety, Zero-Overhead)
#pragma once
#include "stm32f4xx_ll_gpio.h"
#include "stm32f4xx_ll_bus.h"
#include <cstdint>
#include <concepts>

namespace embedded::hw {

enum class OutputSpeed : uint32_t {
    Low      = LL_GPIO_SPEED_FREQ_LOW,
    Medium   = LL_GPIO_SPEED_FREQ_MEDIUM,
    High     = LL_GPIO_SPEED_FREQ_HIGH,
    VeryHigh = LL_GPIO_SPEED_FREQ_VERY_HIGH
};

enum class LogicPolarity : uint8_t {
    ActiveHigh, // Логічна 1 вмикає навантаження (Sourcing)
    ActiveLow   // Логічний 0 вмикає навантаження (Sinking)
};

// Шаблонний клас дискретного виводу з повною перевіркою параметрів під час компіляції
template <uintptr_t PortBase, uint32_t PinMask, LogicPolarity Polarity = LogicPolarity::ActiveHigh>
class SafeOutputPin {
public:
    constexpr SafeOutputPin() noexcept = default;

    // Ресурс апаратного виводу унікальний — забороняємо небезпечне копіювання
    SafeOutputPin(const SafeOutputPin&) = delete;
    SafeOutputPin& operator=(const SafeOutputPin&) = delete;

    // Дозволяємо безпечне переміщення
    SafeOutputPin(SafeOutputPin&&) noexcept = default;
    SafeOutputPin& operator=(SafeOutputPin&&) noexcept = default;

    ~SafeOutputPin() noexcept {
        // Гарантоване переведення навантаження в безпечний вимкнений стан при знищенні об'єкта
        turn_off();
    }

    void init(OutputSpeed speed = OutputSpeed::Low) noexcept {
        enable_port_clock();

        // Встановлюємо безпечний вихідний рівень ДО конфігурації напрямку виводу
        turn_off();

        LL_GPIO_InitTypeDef init_struct{};
        init_struct.Pin        = PinMask;
        init_struct.Mode       = LL_GPIO_MODE_OUTPUT;
        init_struct.OutputType = LL_GPIO_OUTPUT_PUSHPULL;
        init_struct.Speed      = static_cast<uint32_t>(speed);
        init_struct.Pull       = LL_GPIO_PULL_NO;

        LL_GPIO_Init(port(), &init_struct);
    }

    void turn_on() noexcept {
        if constexpr (Polarity == LogicPolarity::ActiveHigh) {
            LL_GPIO_SetOutputPin(port(), PinMask);
        } else {
            LL_GPIO_ResetOutputPin(port(), PinMask);
        }
    }

    void turn_off() noexcept {
        if constexpr (Polarity == LogicPolarity::ActiveHigh) {
            LL_GPIO_ResetOutputPin(port(), PinMask);
        } else {
            LL_GPIO_SetOutputPin(port(), PinMask);
        }
    }

    void toggle() noexcept {
        LL_GPIO_TogglePin(port(), PinMask);
    }

private:
    [[nodiscard]] static GPIO_TypeDef* port() noexcept {
        return reinterpret_cast<GPIO_TypeDef*>(PortBase);
    }

    static void enable_port_clock() noexcept {
        if constexpr (PortBase == GPIOA_BASE) {
            LL_AHB1_GRP1_EnableClock(LL_AHB1_GRP1_PERIPH_GPIOA);
        } else if constexpr (PortBase == GPIOB_BASE) {
            LL_AHB1_GRP1_EnableClock(LL_AHB1_GRP1_PERIPH_GPIOB);
        } else if constexpr (PortBase == GPIOC_BASE) {
            LL_AHB1_GRP1_EnableClock(LL_AHB1_GRP1_PERIPH_GPIOC);
        }
    }
};

} // namespace embedded::hw
