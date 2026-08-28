#include "driver/gpio.h"

#define LED_OUT  15   // якийсь вільний вивід під зовнішній світлодіод
#define BTN_IN   18   // кнопка між цим виводом і GND

static void gpio_init(void)
{
    // вихід
    gpio_config_t out_cfg = {
        .pin_bit_mask = 1ULL << LED_OUT,
        .mode = GPIO_MODE_OUTPUT,
        .pull_up_en = GPIO_PULLUP_DISABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_DISABLE,
    };
    gpio_config(&out_cfg);

    // вхід із підтяжкою вгору
    gpio_config_t in_cfg = {
        .pin_bit_mask = 1ULL << BTN_IN,
        .mode = GPIO_MODE_INPUT,
        .pull_up_en = GPIO_PULLUP_ENABLE,     // тримати лінію на 3.3 В
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_DISABLE,
    };
    gpio_config(&in_cfg);
}

void app_main(void)
{
    gpio_init();
    while (1) {
        // кнопка замикає на GND → 0 = натиснута
        int pressed = (gpio_get_level(BTN_IN) == 0);
        gpio_set_level(LED_OUT, pressed);      // світло, поки тримаєш
        vTaskDelay(pdMS_TO_TICKS(20));
    }
}
