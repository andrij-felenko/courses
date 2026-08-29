/* bsp/bsp_led.h — індикатор стану на платі.
 * Драйвер тримає режим і час, а не ніжку: застосунок каже «тривога»,
 * а не «увімкни PB0 на 150 мілісекунд». */
#ifndef BSP_LED_H
#define BSP_LED_H

#include "hal/hal_gpio.h"

typedef enum {
    BSP_LED_OFF = 0,
    BSP_LED_ON,
    BSP_LED_BLINK_SLOW,  /* штатна робота */
    BSP_LED_BLINK_FAST   /* аварія */
} bsp_led_mode_t;

typedef struct {
    hal_gpio_pin_t pin;
    bsp_led_mode_t mode;
    bool           state;
    uint32_t       last_toggle_ms;
} bsp_led_t;

void bsp_led_init(bsp_led_t *led, const hal_gpio_pin_t *pin);
void bsp_led_set_mode(bsp_led_t *led, bsp_led_mode_t mode);
bsp_led_mode_t bsp_led_mode(const bsp_led_t *led);

/* Викликається з кожним тіком головного циклу. Драйвер не спить і не
 * блокує: він лише порівнює час і за потреби перемикає вивід. */
void bsp_led_tick(bsp_led_t *led, uint32_t now_ms);

#endif /* BSP_LED_H */
