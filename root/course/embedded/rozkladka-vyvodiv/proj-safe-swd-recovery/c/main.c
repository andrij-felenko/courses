#include "clock_safe.h"
#include "safe_gpio.h"
#include "startup_guard.h"

#include "stm32f4xx.h"

#define LED_PIN        5U    /* PA5  — індикатор стану */
#define BACKLIGHT_PIN  8U    /* PA8  — підсвічування дисплея (замість фатального PA13) */

static const gpio_cfg_t OUTPUT_TEMPLATE = {
    .port  = GPIO_PORT_A,
    .pin   = 0U,
    .mode  = GPIO_MODE_OUTPUT,
    .pull  = GPIO_PULL_NONE,
    .speed = GPIO_SPEED_LOW,
    .otype = GPIO_PUSH_PULL,
    .alt   = 0U
};

static void blink(uint32_t times, uint32_t on_ms, uint32_t off_ms)
{
    for (uint32_t i = 0; i < times; ++i) {
        gpio_write(GPIO_PORT_A, LED_PIN, true);
        clock_safe_delay_ms(on_ms);
        gpio_write(GPIO_PORT_A, LED_PIN, false);
        clock_safe_delay_ms(off_ms);
    }
}

int main(void)
{
    /*
     * Захисний інтервал — найперший рядок main(). Усе, що нижче, вже має
     * право вмикати периферію: налагоджувач своє вікно отримав.
     */
    if (startup_guard_run() == GUARD_HELD_BY_OPERATOR) {
        startup_guard_park();   /* не повертається */
    }

    const clock_state_t clk = clock_safe_init();

    gpio_cfg_t led = OUTPUT_TEMPLATE;
    led.pin = LED_PIN;
    if (gpio_configure(&led) != GPIO_OK) {
        startup_guard_park();   /* навіть індикатора немає — далі йти нема сенсу */
    }

    /*
     * Та сама помилка, що вбиває першу партію плат: підсвічування дисплея
     * вішають на PA13. Обгортка відхиляє запит і рахує його.
     */
    gpio_cfg_t backlight = OUTPUT_TEMPLATE;
    backlight.pin = 13U;
    const gpio_status_t rejected = gpio_configure(&backlight);

    /* Робочий вивід, який ні з чим системним не конфліктує. */
    backlight.pin = BACKLIGHT_PIN;
    (void)gpio_configure(&backlight);
    gpio_write(GPIO_PORT_A, BACKLIGHT_PIN, true);

    /*
     * Свідоме перепризначення виглядає так: ключ, робота, повернення виводів
     * шині налагодження. Різниця з аварією — у тому, що воно оборотне.
     */
    if (rejected == GPIO_ERR_SWD_LOCKED) {
        if (gpio_unlock_swd_pins(GPIO_SWD_UNLOCK_KEY)) {
            gpio_cfg_t probe = OUTPUT_TEMPLATE;
            probe.pin = 13U;
            (void)gpio_configure(&probe);
            gpio_write(GPIO_PORT_A, 13U, false);
            clock_safe_delay_ms(1U);
            gpio_restore_swd_pins();   /* PA13/PA14 знову за DAP, замок на місці */
        }
    }

    /*
     * Ритм індикатора одразу каже, на чому ми поїхали:
     * один спалах на секунду — кварц і PLL живі,
     * три коротких — тактування відкотилося на внутрішній генератор.
     */
    for (;;) {
        if (clk.status == CLOCK_OK) {
            blink(1U, 50U, 950U);
        } else {
            blink(3U, 80U, 160U);
            clock_safe_delay_ms(500U);
        }
    }
}
