// ports/stm32f4/stm32_gpio.cpp — виводи STM32F4.
// Регістри MODER, PUPDR і BSRR згадані лише тут; драйвер світлодіода
// отримує hal::OutputPin і не знає навіть номера порту.
#include "ports/stm32f4/stm32_peripherals.hpp"

namespace port {

void Stm32GpioPort::configure(std::uint8_t pin, hal::PinMode mode)
{
    const std::uint32_t shift = static_cast<std::uint32_t>(pin) * 2;

    regs_->MODER &= ~(3U << shift);
    regs_->PUPDR &= ~(3U << shift);

    switch (mode) {
    case hal::PinMode::Input:
        // MODER уже нульовий — це і є вхід.
        break;
    case hal::PinMode::InputPullUp:
        regs_->PUPDR |= (1U << shift);
        break;
    case hal::PinMode::OutputPushPull:
        regs_->MODER  |= (1U << shift);
        regs_->OTYPER &= ~(1U << pin);
        break;
    case hal::PinMode::OutputOpenDrain:
        regs_->MODER  |= (1U << shift);
        regs_->OTYPER |= (1U << pin);
        break;
    }
}

void Stm32GpioPort::set(std::uint8_t pin, bool level)
{
    // Запис у BSRR неподільний: перемикання виводу з головного циклу не
    // зіпсує сусідній вивід, який саме зараз чіпає обробник переривання.
    // Пара «прочитати ODR, змінити біт, записати» такої гарантії не дає.
    regs_->BSRR = level ? (1U << pin) : (1U << (pin + 16U));
}

bool Stm32GpioPort::get(std::uint8_t pin) const
{
    return (regs_->IDR & (1U << pin)) != 0;
}

} // namespace port
