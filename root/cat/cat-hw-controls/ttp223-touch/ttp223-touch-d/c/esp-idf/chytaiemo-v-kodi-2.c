#include "driver/gpio.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_log.h"
#include <inttypes.h>

#define TOUCH_GPIO  GPIO_NUM_4

static const char *TAG = "ttp223";

void app_main(void) {
    gpio_config_t in = {
        .pin_bit_mask = 1ULL << TOUCH_GPIO,
        .mode         = GPIO_MODE_INPUT,
        .pull_up_en   = GPIO_PULLUP_DISABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type    = GPIO_INTR_DISABLE,
    };
    ESP_ERROR_CHECK(gpio_config(&in));

    bool     prev  = false;   // попередній стан входу
    uint32_t count = 0;       // скільки разів торкнулися

    while (1) {
        bool now = gpio_get_level(TOUCH_GPIO) == 1;
        if (now && !prev) {       // щойно був 0, тепер 1 → фронт, момент дотику
            count++;
            ESP_LOGI(TAG, "дотиків: %" PRIu32, count);
        }
        prev = now;
        vTaskDelay(pdMS_TO_TICKS(20));
    }
}
