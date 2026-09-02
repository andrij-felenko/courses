#include "gpio_regs.h"

#include <stddef.h>

#define AHB1_PERIPH_BASE  0x40020000u
#define GPIO_PORT_STRIDE  0x400u
#define RCC_BASE          0x40023800u
#define RCC_AHB1ENR       (*(volatile uint32_t *)(RCC_BASE + 0x30u))

static bool port_ok(gpio_port_t port)
{
    return (unsigned)port < (unsigned)GPIO_PORT_COUNT;
}

static bool pin_ok(uint8_t pin)
{
    return pin < 16u;
}

/* Двобітове поле: MODER, OSPEEDR, PUPDR. */
static void field2_write(volatile uint32_t *reg, uint8_t pin, uint32_t value)
{
    const uint32_t shift = (uint32_t)pin * 2u;
    uint32_t v = *reg;
    v &= ~(3u << shift);
    v |= (value & 3u) << shift;
    *reg = v;
}

static uint32_t field2_read(const volatile uint32_t *reg, uint8_t pin)
{
    return (*reg >> ((uint32_t)pin * 2u)) & 3u;
}

/* Однобітове поле: OTYPER. */
static void field1_write(volatile uint32_t *reg, uint8_t pin, bool set)
{
    const uint32_t mask = 1u << pin;
    if (set) {
        *reg |= mask;
    } else {
        *reg &= ~mask;
    }
}

gpio_regs_t *gpio_port_regs(gpio_port_t port)
{
    if (!port_ok(port)) {
        return NULL;
    }
    return (gpio_regs_t *)(AHB1_PERIPH_BASE + GPIO_PORT_STRIDE * (uint32_t)port);
}

gpio_status_t gpio_clock_enable(gpio_port_t port)
{
    if (!port_ok(port)) {
        return GPIO_ERR_PORT;
    }

    RCC_AHB1ENR |= 1u << (uint32_t)port;

    /* Шина тактування вмикається із затримкою в кілька тактів. Холосте читання
     * гарантує, що наступний запис у регістр порту вже дійде за призначенням. */
    volatile uint32_t sync = RCC_AHB1ENR;
    (void)sync;

    return GPIO_OK;
}

gpio_status_t gpio_pin_configure(gpio_port_t port, uint8_t pin, const gpio_pin_cfg_t *cfg)
{
    if (cfg == NULL) {
        return GPIO_ERR_ARG;
    }
    if (!pin_ok(pin)) {
        return GPIO_ERR_PIN;
    }

    gpio_regs_t *regs = gpio_port_regs(port);
    if (regs == NULL) {
        return GPIO_ERR_PORT;
    }

    const gpio_status_t clk = gpio_clock_enable(port);
    if (clk != GPIO_OK) {
        return clk;
    }

    /* Порядок навмисний: спершу все, що описує ЯК вивід поводитиметься,
     * і аж наприкінці — MODER, тобто вмикання самого каскаду. */
    field2_write(&regs->pupdr,   pin, (uint32_t)cfg->pull);
    field2_write(&regs->ospeedr, pin, (uint32_t)cfg->speed);
    field1_write(&regs->otyper,  pin, cfg->otype == GPIO_TYPE_OPEN_DRAIN);
    field2_write(&regs->moder,   pin, (uint32_t)cfg->mode);

    /* Читаємо назад: якщо конфігурацію порту замкнено через LCKR, запис
     * тихо ігнорується, і без перевірки ми б цього ніколи не помітили. */
    if (field2_read(&regs->moder, pin) != (uint32_t)cfg->mode) {
        return GPIO_ERR_LOCKED;
    }

    return GPIO_OK;
}

gpio_status_t gpio_pin_write(gpio_port_t port, uint8_t pin, bool high)
{
    if (!pin_ok(pin)) {
        return GPIO_ERR_PIN;
    }

    gpio_regs_t *regs = gpio_port_regs(port);
    if (regs == NULL) {
        return GPIO_ERR_PORT;
    }

    /* Один запис — один такт, без читання-модифікації-запису, тож переривання
     * посеред операції не може загубити зміну сусіднього виводу. */
    regs->bsrr = high ? (1u << pin) : (1u << (pin + 16u));
    return GPIO_OK;
}

gpio_status_t gpio_pin_read(gpio_port_t port, uint8_t pin, bool *level)
{
    if (level == NULL) {
        return GPIO_ERR_ARG;
    }
    if (!pin_ok(pin)) {
        return GPIO_ERR_PIN;
    }

    const gpio_regs_t *regs = gpio_port_regs(port);
    if (regs == NULL) {
        return GPIO_ERR_PORT;
    }

    *level = (regs->idr & (1u << pin)) != 0u;
    return GPIO_OK;
}

gpio_status_t gpio_pin_latched(gpio_port_t port, uint8_t pin, bool *level)
{
    if (level == NULL) {
        return GPIO_ERR_ARG;
    }
    if (!pin_ok(pin)) {
        return GPIO_ERR_PIN;
    }

    const gpio_regs_t *regs = gpio_port_regs(port);
    if (regs == NULL) {
        return GPIO_ERR_PORT;
    }

    *level = (regs->odr & (1u << pin)) != 0u;
    return GPIO_OK;
}

void gpio_spin(uint32_t loops)
{
    for (volatile uint32_t i = 0; i < loops; ++i) {
        /* volatile не дає оптимізатору викинути цикл */
    }
}

const char *gpio_status_text(gpio_status_t st)
{
    switch (st) {
    case GPIO_OK:         return "ok";
    case GPIO_ERR_PORT:   return "немає такого порту";
    case GPIO_ERR_PIN:    return "номер виводу поза 0..15";
    case GPIO_ERR_LOCKED: return "конфігурацію порту замкнено (LCKR)";
    case GPIO_ERR_ARG:    return "некоректний аргумент";
    default:              return "невідома помилка";
    }
}
