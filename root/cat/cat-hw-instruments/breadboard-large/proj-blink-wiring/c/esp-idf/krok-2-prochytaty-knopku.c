#include "driver/gpio.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define PIN_LED  GPIO_NUM_18
#define PIN_BTN  GPIO_NUM_19     // ніжка IN зі схеми: сюди одна нога кнопки, друга — на «−»

void app_main(void) {
    gpio_config_t out = {
        .pin_bit_mask = 1ULL << PIN_LED,
        .mode = GPIO_MODE_OUTPUT,
    };
    gpio_config(&out);

    gpio_config_t in = {
        .pin_bit_mask = 1ULL << PIN_BTN,
        .mode = GPIO_MODE_INPUT,
        .pull_up_en = GPIO_PULLUP_ENABLE,   // вхід + внутрішня підтяжка до «+»
    };
    gpio_config(&in);

    while (1) {
        // active-low: натиснуто = 0. Тож "світло є" ⇔ "на вході 0".
        if (gpio_get_level(PIN_BTN) == 0) {
            gpio_set_level(PIN_LED, 1);     // кнопку тримають → світимо
        } else {
            gpio_set_level(PIN_LED, 0);     // відпущено → гасимо
        }
        vTaskDelay(pdMS_TO_TICKS(5));       // опитуємо часто, але віддаємо час іншим задачам
    }
}
