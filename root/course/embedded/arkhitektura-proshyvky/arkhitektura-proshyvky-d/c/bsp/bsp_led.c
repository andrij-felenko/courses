/* bsp/bsp_led.c — реалізація індикатора. */
#include "bsp/bsp_led.h"

#include "include/sys_config.h"

static void apply(bsp_led_t *led, bool on)
{
    led->state = on;
    hal_gpio_write(&led->pin, on);
}

void bsp_led_init(bsp_led_t *led, const hal_gpio_pin_t *pin)
{
    if (led == 0 || pin == 0) {
        return;
    }
    led->pin            = *pin;
    led->mode           = BSP_LED_OFF;
    led->state          = false;
    led->last_toggle_ms = 0u;

    hal_gpio_configure(&led->pin, HAL_GPIO_MODE_OUTPUT_PP);
    apply(led, false);
}

void bsp_led_set_mode(bsp_led_t *led, bsp_led_mode_t mode)
{
    if (led == 0 || led->mode == mode) {
        return;
    }
    led->mode = mode;

    if (mode == BSP_LED_OFF) {
        apply(led, false);
    } else if (mode == BSP_LED_ON) {
        apply(led, true);
    } else {
        /* Миготіння починаємо з увімкненого стану, щоб зміна режиму
         * була видима оком одразу, а не через півперіоду. */
        apply(led, true);
        led->last_toggle_ms = 0u;
    }
}

bsp_led_mode_t bsp_led_mode(const bsp_led_t *led)
{
    return (led != 0) ? led->mode : BSP_LED_OFF;
}

void bsp_led_tick(bsp_led_t *led, uint32_t now_ms)
{
    if (led == 0 || led->mode == BSP_LED_OFF || led->mode == BSP_LED_ON) {
        return;
    }

    const uint32_t period_ms = (led->mode == BSP_LED_BLINK_FAST)
                                   ? SYS_LED_BLINK_FAST_MS
                                   : SYS_LED_BLINK_SLOW_MS;

    if (led->last_toggle_ms == 0u) {
        led->last_toggle_ms = now_ms;
        return;
    }

    /* Різниця, а не порівняння самих міток: так перемикання переживає
     * переповнення лічильника мілісекунд на сорок дев'ятій добі. */
    if ((now_ms - led->last_toggle_ms) >= (period_ms / 2u)) {
        led->last_toggle_ms = now_ms;
        apply(led, !led->state);
    }
}
