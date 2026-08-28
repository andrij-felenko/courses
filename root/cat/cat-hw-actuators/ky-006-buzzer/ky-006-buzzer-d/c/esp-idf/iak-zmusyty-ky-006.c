#include "driver/gpio.h"
#include "esp_rom_sys.h"        // esp_rom_delay_us — затримка на мікросекунди

#define BUZ_GPIO GPIO_NUM_18

void buzz_1khz(void)
{
    gpio_config_t cfg = {
        .pin_bit_mask = 1ULL << BUZ_GPIO,
        .mode         = GPIO_MODE_OUTPUT,
        .pull_up_en   = GPIO_PULLUP_DISABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type    = GPIO_INTR_DISABLE,
    };
    ESP_ERROR_CHECK(gpio_config(&cfg));

    while (1) {
        // один цикл меандру 1000 Гц: 500 мкс вгорі + 500 мкс унизу
        gpio_set_level(BUZ_GPIO, 1);
        esp_rom_delay_us(500);
        gpio_set_level(BUZ_GPIO, 0);
        esp_rom_delay_us(500);
    }
}
