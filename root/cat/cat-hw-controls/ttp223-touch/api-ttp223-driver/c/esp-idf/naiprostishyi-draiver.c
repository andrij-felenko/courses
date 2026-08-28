#include "driver/gpio.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define PIN_TOUCH  GPIO_NUM_4          // SIG давача TTP223
static const char *TAG = "ttp223";

void app_main(void) {
    gpio_config_t cfg = {
        .pin_bit_mask = 1ULL << PIN_TOUCH,
        .mode         = GPIO_MODE_INPUT,
        .pull_up_en   = GPIO_PULLUP_DISABLE,     // вихід двотактний → без підтяжок
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type    = GPIO_INTR_DISABLE,
    };
    ESP_ERROR_CHECK(gpio_config(&cfg));

    while (1) {
        bool touched = (gpio_get_level(PIN_TOUCH) == 1);   // активний у 1
        ESP_LOGI(TAG, "%s", touched ? "палець" : "-");
        vTaskDelay(pdMS_TO_TICKS(100));
    }
}
