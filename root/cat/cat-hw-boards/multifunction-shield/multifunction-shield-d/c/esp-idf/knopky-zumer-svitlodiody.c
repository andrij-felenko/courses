#include "driver/gpio.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define S1    GPIO_NUM_18   // кнопка 1
#define LED1  GPIO_NUM_19   // світлодіод 1 (активний низьким!)

void app_main(void) {
    gpio_config_t btn = {
        .pin_bit_mask = 1ULL << S1,
        .mode         = GPIO_MODE_INPUT,
        .pull_up_en   = GPIO_PULLUP_ENABLE,   // у спокої 1, натиснута — 0
    };
    gpio_config(&btn);

    gpio_config_t led = {
        .pin_bit_mask = 1ULL << LED1,
        .mode         = GPIO_MODE_OUTPUT,
    };
    gpio_config(&led);
    gpio_set_level(LED1, 1);                  // 1 = згашено

    while (1) {
        if (gpio_get_level(S1) == 0)          // кнопку натиснуто
            gpio_set_level(LED1, 0);          // 0 = світиться
        else
            gpio_set_level(LED1, 1);          // відпустив — гасне
        vTaskDelay(pdMS_TO_TICKS(10));
    }
}
