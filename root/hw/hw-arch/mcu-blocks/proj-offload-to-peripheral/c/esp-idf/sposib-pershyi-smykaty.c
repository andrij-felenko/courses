#include "driver/gpio.h"
#include "esp_rom_sys.h"       // esp_rom_delay_us()

#define PIN GPIO_NUM_18

void bitbang_task(void *arg) {
  gpio_config_t io = { .pin_bit_mask = 1ULL << PIN, .mode = GPIO_MODE_OUTPUT };
  gpio_config(&io);
  for (;;) {
    // ШІМ ~1 кГц, шпаруватість 50 %: 500 мкс «1», 500 мкс «0»
    gpio_set_level(PIN, 1);
    esp_rom_delay_us(500);
    gpio_set_level(PIN, 0);
    esp_rom_delay_us(500);
  }
}
