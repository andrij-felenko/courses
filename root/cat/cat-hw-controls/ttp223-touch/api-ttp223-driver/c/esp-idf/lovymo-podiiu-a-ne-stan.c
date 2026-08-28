#include "driver/gpio.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define PIN_TOUCH  GPIO_NUM_4
static const char *TAG = "ttp223";

void app_main(void) {
    gpio_config_t cfg = {
        .pin_bit_mask = 1ULL << PIN_TOUCH,
        .mode         = GPIO_MODE_INPUT,
        .pull_up_en   = GPIO_PULLUP_DISABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type    = GPIO_INTR_DISABLE,
    };
    ESP_ERROR_CHECK(gpio_config(&cfg));

    bool     prev  = false;        // стан входу з минулого проходу циклу
    uint32_t count = 0;

    while (1) {
        bool now = (gpio_get_level(PIN_TOUCH) == 1);

        if (now && !prev)          // було 0, стало 1 → передній фронт = момент дотику
            ESP_LOGI(TAG, "дотиків: %u", (unsigned)++count);
        // if (!now && prev) { … } // тут ловився б задній фронт = момент відпускання

        prev = now;                // запам'ятали для наступного проходу
        vTaskDelay(pdMS_TO_TICKS(20));
    }
}
