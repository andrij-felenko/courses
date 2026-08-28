#include "driver/gpio.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define BTN GPIO_NUM_0   // вивід, до якого підключена кнопка
#define LED GPIO_NUM_2   // вивід зі світлодіодом

void app_main(void) {
    gpio_config_t btn = {
        .pin_bit_mask = 1ULL << BTN,
        .mode         = GPIO_MODE_INPUT,
        .pull_up_en   = GPIO_PULLUP_ENABLE,   // підтяжка тримає вхід у «1»
    };
    gpio_config(&btn);

    gpio_config_t led = {
        .pin_bit_mask = 1ULL << LED,
        .mode         = GPIO_MODE_OUTPUT,
    };
    gpio_config(&led);

    while (1) {
        // кнопка притискає вхід до «0» → натиск = 0
        bool pressed = (gpio_get_level(BTN) == 0);
        gpio_set_level(LED, pressed ? 1 : 0);
        vTaskDelay(pdMS_TO_TICKS(10));
    }
}
