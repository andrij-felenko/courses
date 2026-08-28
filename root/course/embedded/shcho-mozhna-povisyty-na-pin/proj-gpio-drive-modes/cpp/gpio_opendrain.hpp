// Файл: gpio_opendrain.hpp — Ідіоматичний C++20 Open-Drain драйвер
#pragma once
#include "stm32f4xx_ll_gpio.h"
#include <concepts>

namespace embedded::hw {

template <uintptr_t PortBase, uint32_t PinMask>
class OpenDrainLine {
public:
    static void init(OutputSpeed speed = OutputSpeed::Medium) noexcept {
        auto* port = reinterpret_cast<GPIO_TypeDef*>(PortBase);

        LL_GPIO_InitTypeDef init{};
        init.Pin        = PinMask;
        init.Mode       = LL_GPIO_MODE_OUTPUT;
        init.OutputType = LL_GPIO_OUTPUT_OPENDRAIN;
        init.Speed      = static_cast<uint32_t>(speed);
        init.Pull       = LL_GPIO_PULL_NO;

        LL_GPIO_Init(port, &init);
        release_bus();
    }

    // Притягнути лінію до землі (активний стан 0 В)
    static void drive_low() noexcept {
        LL_GPIO_ResetOutputPin(reinterpret_cast<GPIO_TypeDef*>(PortBase), PinMask);
    }

    // Відпустити лінію у Hi-Z (високий рівень забезпечує зовнішній Pull-Up резистор)
    static void release_bus() noexcept {
        LL_GPIO_SetOutputPin(reinterpret_cast<GPIO_TypeDef*>(PortBase), PinMask);
    }
};

} // namespace embedded::hw
