#include "driver/gpio.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define PIR GPIO_NUM_4     // OUT давача
#define LED GPIO_NUM_2     // світлодіод плати

static const char *TAG = "pir";

void app_main(void) {
    gpio_config_t in = {
        .pin_bit_mask  = 1ULL << PIR,
        .mode          = GPIO_MODE_INPUT,
        .pull_up_en    = GPIO_PULLUP_DISABLE,    // вихід давача сам штовхає рівень
        .pull_down_en  = GPIO_PULLDOWN_DISABLE,
        .intr_type     = GPIO_INTR_DISABLE,
    };
    ESP_ERROR_CHECK(gpio_config(&in));
    ESP_ERROR_CHECK(gpio_set_direction(LED, GPIO_MODE_OUTPUT));

    while (1) {
        int motion = gpio_get_level(PIR);        // 1 = є рух, 0 = немає
        gpio_set_level(LED, motion);
        if (motion) ESP_LOGI(TAG, "рух!");
        vTaskDelay(pdMS_TO_TICKS(50));
    }
}
