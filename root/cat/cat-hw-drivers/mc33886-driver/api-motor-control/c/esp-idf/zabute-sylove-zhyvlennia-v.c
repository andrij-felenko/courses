// Те саме на ESP-IDF: вхід із підтяжкою вгору, активно-низький рівень.
#include "driver/gpio.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define PIN_FS  GPIO_NUM_15
static const char *TAG = "mc33886";

void app_main(void) {
    gpio_config_t io = {
        .pin_bit_mask = 1ULL << PIN_FS,
        .mode = GPIO_MODE_INPUT,
        .pull_up_en = GPIO_PULLUP_ENABLE,   // якщо зовнішньої підтяжки нема
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_DISABLE,
    };
    ESP_ERROR_CHECK(gpio_config(&io));

    for (;;) {
        if (gpio_get_level(PIN_FS) == 0) {
            // Драйвер сам знеструмив міст і сигналить біду.
            // Найчастіша причина при першому запуску — V+ без напруги
            // або просадка живлення; далі — перегрів чи КЗ на виході.
            ESP_LOGE(TAG, "FAULT (перевір V+, землю, струм, нагрів)");
            vTaskDelay(pdMS_TO_TICKS(500));
        }
        vTaskDelay(pdMS_TO_TICKS(10));
    }
}
