#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/gpio.h"

#define LED_PIN  GPIO_NUM_2          // ніжку звіряємо з платою

void app_main(void) {
    gpio_reset_pin(LED_PIN);
    gpio_set_direction(LED_PIN, GPIO_MODE_OUTPUT);
    for (;;) {
        gpio_set_level(LED_PIN, 1);  // увімкнути
        vTaskDelay(pdMS_TO_TICKS(500));
        gpio_set_level(LED_PIN, 0);  // вимкнути
        vTaskDelay(pdMS_TO_TICKS(500));
    }
}
