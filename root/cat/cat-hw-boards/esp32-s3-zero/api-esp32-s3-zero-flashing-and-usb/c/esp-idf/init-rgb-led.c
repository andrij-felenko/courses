#include "driver/rmt_tx.h"
#include "led_strip.h"

#define RGB_LED_GPIO 21

static led_strip_handle_t led_strip;

void init_rgb_led(void) {
    led_strip_config_t strip_config = {
        .strip_gpio_num = RGB_LED_GPIO,
        .max_leds = 1,
    };
    led_strip_rmt_config_t rmt_config = {
        .resolution_hz = 10 * 1000 * 1000, // 10MHz
    };
    ESP_ERROR_CHECK(led_strip_new_rmt_device(&strip_config, &rmt_config, &led_strip));
    led_strip_clear(led_strip);
}

void set_rgb_color(uint8_t red, uint8_t green, uint8_t blue) {
    led_strip_set_pixel(led_strip, 0, red, green, blue);
    led_strip_refresh(led_strip);
}
