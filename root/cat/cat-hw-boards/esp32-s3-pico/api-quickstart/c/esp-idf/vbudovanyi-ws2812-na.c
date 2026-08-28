#include "led_strip.h"

void app_main(void) {
  led_strip_handle_t strip;
  led_strip_config_t cfg = { .strip_gpio_num = 21, .max_leds = 1 };
  led_strip_rmt_config_t rmt = { .resolution_hz = 10 * 1000 * 1000 };  // крок 100 нс
  ESP_ERROR_CHECK(led_strip_new_rmt_device(&cfg, &rmt, &strip));

  led_strip_set_pixel(strip, 0, 0, 40, 0);   // r, g, b — кожен 0..255
  led_strip_refresh(strip);                  // тьмяно-зелений: «плата ожила»

  while (1) {
    led_strip_set_pixel(strip, 0, 40, 0, 0); // червоний
    led_strip_refresh(strip);                // кадр іде в RMT
    vTaskDelay(pdMS_TO_TICKS(500));
    led_strip_set_pixel(strip, 0, 0, 0, 40); // синій
    led_strip_refresh(strip);
    vTaskDelay(pdMS_TO_TICKS(500));
  }
}
