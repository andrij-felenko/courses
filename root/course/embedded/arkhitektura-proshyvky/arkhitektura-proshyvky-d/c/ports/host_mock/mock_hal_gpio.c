/* ports/host_mock/mock_hal_gpio.c — виводи, яких немає.
 * Замість регістра BSRR — слово в пам'яті плюс лічильник перемикань.
 * Тест питає «скільки разів блимнув світлодіод за десять секунд» і
 * розрізняє штатний режим від аварійного, не маючи ані плати, ані ока. */
#include "ports/host_mock/host_port.h"

#define MOCK_GPIO_PINS   16u

typedef struct {
    bool     level[MOCK_GPIO_PINS];
    unsigned toggles[MOCK_GPIO_PINS];
    hal_gpio_mode_t mode[MOCK_GPIO_PINS];
} mock_gpio_port_t;

static mock_gpio_port_t g_port;

static void mock_gpio_configure(void *ctx, uint8_t pin, hal_gpio_mode_t mode)
{
    mock_gpio_port_t *port = (mock_gpio_port_t *)ctx;
    if (pin < MOCK_GPIO_PINS) {
        port->mode[pin] = mode;
    }
}

static void mock_gpio_set(void *ctx, uint8_t pin, bool level)
{
    mock_gpio_port_t *port = (mock_gpio_port_t *)ctx;
    if (pin >= MOCK_GPIO_PINS) {
        return;
    }
    if (port->level[pin] != level) {
        port->toggles[pin]++;
    }
    port->level[pin] = level;
}

static bool mock_gpio_get(void *ctx, uint8_t pin)
{
    const mock_gpio_port_t *port = (const mock_gpio_port_t *)ctx;
    return (pin < MOCK_GPIO_PINS) ? port->level[pin] : false;
}

static const hal_gpio_ops_t g_mock_gpio_ops = {
    .configure = mock_gpio_configure,
    .set       = mock_gpio_set,
    .get       = mock_gpio_get,
};

const hal_gpio_ops_t *mock_gpio_ops(void)
{
    return &g_mock_gpio_ops;
}

void *mock_gpio_port(void)
{
    return &g_port;
}

bool mock_gpio_level(uint8_t pin)
{
    return (pin < MOCK_GPIO_PINS) ? g_port.level[pin] : false;
}

unsigned mock_gpio_toggle_count(uint8_t pin)
{
    return (pin < MOCK_GPIO_PINS) ? g_port.toggles[pin] : 0u;
}
