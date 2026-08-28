#include "driver/gpio.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define TILT GPIO_NUM_4    // пін S давача
#define LED  GPIO_NUM_2    // світлодіод плати

static const char *TAG = "tilt";

void app_main(void) {
    gpio_config_t in = {
        .pin_bit_mask = 1ULL << TILT,
        .mode         = GPIO_MODE_INPUT,
        .pull_up_en   = GPIO_PULLUP_DISABLE,   // підтяжка 10 кОм уже на модулі
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type    = GPIO_INTR_DISABLE,
    };
    ESP_ERROR_CHECK(gpio_config(&in));
    ESP_ERROR_CHECK(gpio_set_direction(LED, GPIO_MODE_OUTPUT));

    while (1) {
        // УВАГА: логіка перевернута — нахил дає 0, спокій 1
        int tilted = (gpio_get_level(TILT) == 0);
        gpio_set_level(LED, tilted);           // світимо, поки нахилено
        if (tilted) ESP_LOGI(TAG, "нахил!");
        vTaskDelay(pdMS_TO_TICKS(50));
    }
}
