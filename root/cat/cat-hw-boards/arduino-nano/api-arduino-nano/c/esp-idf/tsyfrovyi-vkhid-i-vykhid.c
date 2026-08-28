#include "driver/gpio.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define PIN_BTN GPIO_NUM_4      // кнопка між GPIO4 і GND
#define PIN_LED GPIO_NUM_2

void app_main(void) {
    const gpio_config_t btn = {
        .pin_bit_mask = 1ULL << PIN_BTN,
        .mode         = GPIO_MODE_INPUT,
        .pull_up_en   = GPIO_PULLUP_ENABLE,   // вільний стан = 1, натиск = 0
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type    = GPIO_INTR_DISABLE,
    };
    ESP_ERROR_CHECK(gpio_config(&btn));
    gpio_set_direction(PIN_LED, GPIO_MODE_OUTPUT);

    while (1) {
        bool pressed = (gpio_get_level(PIN_BTN) == 0);  // натиснуто = замкнуто на GND
        gpio_set_level(PIN_LED, pressed);
        vTaskDelay(pdMS_TO_TICKS(10));
    }
}
