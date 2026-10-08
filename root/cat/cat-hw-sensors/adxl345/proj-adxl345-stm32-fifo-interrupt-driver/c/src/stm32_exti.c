#include "stm32_exti.h"
#include <stddef.h>

static volatile bool g_watermark_event = false;
static uint16_t g_configured_pin = 0;

void stm32_exti_init(const stm32_exti_config_t *config)
{
    if (config == NULL) {
        return;
    }

    g_configured_pin = config->gpio_pin;
    g_watermark_event = false;
}

bool stm32_exti_has_watermark_flag(void)
{
    return g_watermark_event;
}

void stm32_exti_clear_watermark_flag(void)
{
    g_watermark_event = false;
}

void stm32_exti_gpio_isr_handler(uint16_t gpio_pin)
{
    if (gpio_pin == g_configured_pin) {
        g_watermark_event = true;
    }
}
