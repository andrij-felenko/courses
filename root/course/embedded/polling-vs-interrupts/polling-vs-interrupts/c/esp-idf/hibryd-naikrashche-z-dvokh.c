#include "driver/gpio.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define SENSOR_PIN GPIO_NUM_4

volatile uint32_t turns = 0;

void app_main(void) {
    gpio_config_t cfg = {
        .pin_bit_mask = 1ULL << SENSOR_PIN,
        .mode = GPIO_MODE_INPUT,
        .pull_up_en = GPIO_PULLUP_ENABLE,
    };
    gpio_config(&cfg);

    int prev = 0;
    while (1) {
        int now = gpio_get_level(SENSOR_PIN);  // питаємо ніжку самі
        if (!prev && now)                      // зловили висхідний фронт?
            turns++;
        prev = now;
        vTaskDelay(pdMS_TO_TICKS(5));          // ... решта роботи циклу ...
    }
}
