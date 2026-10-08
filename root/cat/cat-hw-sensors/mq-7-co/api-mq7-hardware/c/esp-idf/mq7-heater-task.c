// Керування двофазним циклом живлення нагрівача MQ-7 для ESP-IDF
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/gpio.h"
#include "esp_log.h"

#define HEATER_GPIO GPIO_NUM_18
static const char *TAG = "MQ7_DRIVER";

void mq7_heater_task(void *pvParameters) {
    gpio_config_t io_conf = {
        .pin_bit_mask = (1ULL << HEATER_GPIO),
        .mode = GPIO_MODE_OUTPUT,
        .pull_down_en = 0,
        .pull_up_en = 0,
        .intr_type = GPIO_INTR_DISABLE
    };
    gpio_config(&io_conf);

    while (1) {
        // Фаза 1: Очищення 5 В протягом 60 секунд
        ESP_LOGI(TAG, "Старт фази очищення (5 В, 60 с)");
        gpio_set_level(HEATER_GPIO, 1);
        vTaskDelay(pdMS_TO_TICKS(60000));

        // Фаза 2: Вимірювання 1.4 В протягом 90 секунд
        ESP_LOGI(TAG, "Старт фази вимірювання (1.4 В, 90 с)");
        gpio_set_level(HEATER_GPIO, 0);
        vTaskDelay(pdMS_TO_TICKS(90000));

        // У цей момент зчитують дані АЦП з виходу AOUT
        ESP_LOGI(TAG, "Фаза вимірювання завершена, зчитування АЦП");
    }
}
