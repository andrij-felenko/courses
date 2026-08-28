#include "driver/gpio.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

void blink(int times, int ms) {
    for (int i = 0; i < times; i++) {
        gpio_set_level(LED, 1);            // ніжку у високий рівень
        vTaskDelay(pdMS_TO_TICKS(ms));
        gpio_set_level(LED, 0);            // і назад у низький
        vTaskDelay(pdMS_TO_TICKS(ms));
    }
}
