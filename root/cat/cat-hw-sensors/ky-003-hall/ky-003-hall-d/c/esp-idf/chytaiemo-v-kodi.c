#include "driver/gpio.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_log.h"

#define HALL  GPIO_NUM_4           // S давача KY-003
#define LED   GPIO_NUM_2           // світлодіод на платі
static const char *TAG = "hall";

void app_main(void) {
    gpio_config_t in = {
        .pin_bit_mask = 1ULL << HALL,
        .mode         = GPIO_MODE_INPUT,
        .pull_up_en   = GPIO_PULLUP_ENABLE,    // без підтяжки нога висить — читатимеш сміття
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type    = GPIO_INTR_DISABLE,
    };
    ESP_ERROR_CHECK(gpio_config(&in));
    gpio_config_t out = { .pin_bit_mask = 1ULL << LED, .mode = GPIO_MODE_OUTPUT };
    ESP_ERROR_CHECK(gpio_config(&out));

    // давач живиться від 5 В, але вихід у нього відкритий колектор:
    // рівень «1» задає підтяжка на 3.3 В, тож нозі ESP32 нічого не загрожує
    while (1) {
        bool magnet = (gpio_get_level(HALL) == 0);   // активний у нулі: 0 = є магніт
        gpio_set_level(LED, magnet);
        if (magnet) ESP_LOGI(TAG, "магніт!");
        vTaskDelay(pdMS_TO_TICKS(50));
    }
}
