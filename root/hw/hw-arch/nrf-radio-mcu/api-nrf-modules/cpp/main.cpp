#include <stdint.h>
#include "nrf_gpio.h"   /* nRF5 SDK: nrfx або legacy nrf_gpio */

#define LED_PIN   17    /* P0.17 — типовий LED на багатьох nRF52-модулях */

static void delay_ms(uint32_t ms) {
    /* Проста затримка-заглушка; у реальному firmware — nrfx_coredep_delay */
    volatile uint32_t n = ms * 6400u;
    while (n--) __NOP();
}

int main(void) {
    /* Конфігуруємо пін як вихід */
    nrf_gpio_cfg_output(LED_PIN);

    while (1) {
        nrf_gpio_pin_toggle(LED_PIN);   /* інвертуємо: 0→1→0→… */
        delay_ms(500);
        /* Блимає = живлення, кварц 32 МГц, ядро й прошивка — живі.
           BLE-стек вмикається окремо поверх цього каркасу. */
    }
}
