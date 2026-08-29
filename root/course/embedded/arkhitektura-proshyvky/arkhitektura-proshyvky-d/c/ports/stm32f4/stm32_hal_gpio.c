/* ports/stm32f4/stm32_hal_gpio.c — виводи STM32F4 за таблицею операцій.
 * Регістри BSRR, MODER і PUPDR згадані лише тут. Драйвер світлодіода
 * отримує заповнений hal_gpio_pin_t і не знає навіть номера порту. */
#include "hal/hal_gpio.h"
#include "ports/stm32f4/stm32_port.h"

#include "stm32f4xx.h"

static void stm32_gpio_configure(void *ctx, uint8_t pin, hal_gpio_mode_t mode)
{
    GPIO_TypeDef *port = (GPIO_TypeDef *)ctx;
    const uint32_t shift = (uint32_t)pin * 2u;

    port->MODER &= ~(3u << shift);
    port->PUPDR &= ~(3u << shift);

    switch (mode) {
    case HAL_GPIO_MODE_INPUT:
        /* MODER уже нульовий — це і є вхід. */
        break;

    case HAL_GPIO_MODE_INPUT_PULLUP:
        port->PUPDR |= (1u << shift);
        break;

    case HAL_GPIO_MODE_OUTPUT_PP:
        port->MODER  |= (1u << shift);
        port->OTYPER &= ~(1u << pin);
        break;

    case HAL_GPIO_MODE_OUTPUT_OD:
        port->MODER  |= (1u << shift);
        port->OTYPER |= (1u << pin);
        break;

    default:
        break;
    }
}

static void stm32_gpio_set(void *ctx, uint8_t pin, bool level)
{
    GPIO_TypeDef *port = (GPIO_TypeDef *)ctx;

    /* Запис у BSRR неподільний: перемикання виводу з головного циклу не
     * зіпсує сусідній вивід, який саме зараз чіпає обробник переривання.
     * Пара «прочитати ODR, змінити біт, записати» такої гарантії не дає. */
    if (level) {
        port->BSRR = (uint32_t)1u << pin;
    } else {
        port->BSRR = (uint32_t)1u << (pin + 16u);
    }
}

static bool stm32_gpio_get(void *ctx, uint8_t pin)
{
    const GPIO_TypeDef *port = (const GPIO_TypeDef *)ctx;
    return (port->IDR & ((uint32_t)1u << pin)) != 0u;
}

static const hal_gpio_ops_t g_stm32_gpio_ops = {
    .configure = stm32_gpio_configure,
    .set       = stm32_gpio_set,
    .get       = stm32_gpio_get,
};

const hal_gpio_ops_t *stm32_gpio_ops(void)
{
    return &g_stm32_gpio_ops;
}

void *stm32_gpio_port_b(void)
{
    RCC->AHB1ENR |= RCC_AHB1ENR_GPIOBEN;
    return GPIOB;
}
