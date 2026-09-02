#include "safe_gpio.h"

#include "stm32f4xx.h"

#include <stddef.h>

static GPIO_TypeDef *const PORT_REGS[GPIO_PORT_COUNT] = {
    GPIOA, GPIOB, GPIOC, GPIOD, GPIOE
};

static const uint32_t PORT_CLOCK[GPIO_PORT_COUNT] = {
    RCC_AHB1ENR_GPIOAEN, RCC_AHB1ENR_GPIOBEN, RCC_AHB1ENR_GPIOCEN,
    RCC_AHB1ENR_GPIODEN, RCC_AHB1ENR_GPIOEEN
};

static bool     s_swd_unlocked  = false;
static uint32_t s_rejected      = 0U;

bool gpio_is_swd_pin(gpio_port_t port, uint8_t pin)
{
    /*
     * PA15/PB3/PB4 — це JTDI/JTDO/NJTRST: у чистому SWD вони вільні,
     * тому в замок не входять. Заборонені лише дві лінії самого SWD.
     */
    return (port == GPIO_PORT_A) && ((pin == 13U) || (pin == 14U));
}

static void port_clock_enable(gpio_port_t port)
{
    RCC->AHB1ENR |= PORT_CLOCK[port];
    (void)RCC->AHB1ENR;   /* зворотне читання перед першим доступом до регістрів порту */
}

/* Двобітове поле: MODER, PUPDR, OSPEEDR. */
static void set_pair_field(volatile uint32_t *reg, uint8_t pin, uint32_t value)
{
    const uint32_t shift = (uint32_t)pin * 2U;
    uint32_t v = *reg;

    v &= ~(0x3UL << shift);
    v |=  ((value & 0x3UL) << shift);
    *reg = v;
}

static void set_alternate(GPIO_TypeDef *regs, uint8_t pin, uint8_t alt)
{
    const uint32_t idx   = (uint32_t)pin >> 3U;          /* AFR[0] для 0..7, AFR[1] для 8..15 */
    const uint32_t shift = ((uint32_t)pin & 0x7UL) * 4U;
    uint32_t v = regs->AFR[idx];

    v &= ~(0xFUL << shift);
    v |=  ((uint32_t)alt << shift);
    regs->AFR[idx] = v;
}

static void apply(GPIO_TypeDef *regs, const gpio_cfg_t *cfg)
{
    /*
     * Порядок важить: спершу все, що описує майбутній стан лінії, і лише
     * останнім — MODER. Інакше вивід на мить стане виходом зі старою
     * альтернативною функцією й видасть на плату голку.
     */
    set_alternate(regs, cfg->pin, cfg->alt);
    set_pair_field(&regs->OSPEEDR, cfg->pin, (uint32_t)cfg->speed);
    set_pair_field(&regs->PUPDR,   cfg->pin, (uint32_t)cfg->pull);

    if (cfg->otype == GPIO_OPEN_DRAIN) {
        regs->OTYPER |= (1UL << cfg->pin);
    } else {
        regs->OTYPER &= ~(1UL << cfg->pin);
    }

    set_pair_field(&regs->MODER, cfg->pin, (uint32_t)cfg->mode);
}

gpio_status_t gpio_configure(const gpio_cfg_t *cfg)
{
    if ((cfg == NULL) || (cfg->port >= GPIO_PORT_COUNT)) {
        return GPIO_ERR_PORT;
    }
    if (cfg->pin > 15U) {
        return GPIO_ERR_PIN;
    }
    if (cfg->alt > 15U) {
        return GPIO_ERR_ALT;
    }
    if (gpio_is_swd_pin(cfg->port, cfg->pin) && !s_swd_unlocked) {
        ++s_rejected;
        return GPIO_ERR_SWD_LOCKED;
    }

    port_clock_enable(cfg->port);
    apply(PORT_REGS[cfg->port], cfg);
    return GPIO_OK;
}

bool gpio_unlock_swd_pins(uint32_t key)
{
    if (key != GPIO_SWD_UNLOCK_KEY) {
        return false;
    }
    s_swd_unlocked = true;
    return true;
}

void gpio_restore_swd_pins(void)
{
    /* Заводський стан після скидання: AF0, SWDIO з підтяжкою вгору, SWCLK — вниз. */
    static const gpio_cfg_t swdio = {
        .port = GPIO_PORT_A, .pin = 13U, .mode = GPIO_MODE_ALT,
        .pull = GPIO_PULL_UP, .speed = GPIO_SPEED_VERY_HIGH,
        .otype = GPIO_PUSH_PULL, .alt = 0U
    };
    static const gpio_cfg_t swclk = {
        .port = GPIO_PORT_A, .pin = 14U, .mode = GPIO_MODE_ALT,
        .pull = GPIO_PULL_DOWN, .speed = GPIO_SPEED_VERY_HIGH,
        .otype = GPIO_PUSH_PULL, .alt = 0U
    };

    port_clock_enable(GPIO_PORT_A);
    apply(PORT_REGS[GPIO_PORT_A], &swdio);
    apply(PORT_REGS[GPIO_PORT_A], &swclk);

    /* Замок повертаємо на місце: наступна випадкова спроба знову буде відхилена. */
    s_swd_unlocked = false;
}

uint32_t gpio_rejected_count(void)
{
    return s_rejected;
}

void gpio_write(gpio_port_t port, uint8_t pin, bool level)
{
    if ((port >= GPIO_PORT_COUNT) || (pin > 15U)) {
        return;
    }
    /* BSRR: атомарна установка (молодша половина) і скидання (старша). */
    PORT_REGS[port]->BSRR = level ? (1UL << pin) : (1UL << (pin + 16U));
}

bool gpio_read(gpio_port_t port, uint8_t pin)
{
    if ((port >= GPIO_PORT_COUNT) || (pin > 15U)) {
        return false;
    }
    return (PORT_REGS[port]->IDR & (1UL << pin)) != 0U;
}

void gpio_toggle(gpio_port_t port, uint8_t pin)
{
    if ((port >= GPIO_PORT_COUNT) || (pin > 15U)) {
        return;
    }
    PORT_REGS[port]->ODR ^= (1UL << pin);
}

const char *gpio_status_str(gpio_status_t status)
{
    switch (status) {
    case GPIO_OK:             return "ok";
    case GPIO_ERR_PORT:       return "немає такого порту";
    case GPIO_ERR_PIN:        return "номер виводу поза межами";
    case GPIO_ERR_ALT:        return "немає такої альтернативної функції";
    case GPIO_ERR_SWD_LOCKED: return "вивід належить шині SWD";
    default:                  return "невідомий стан";
    }
}
