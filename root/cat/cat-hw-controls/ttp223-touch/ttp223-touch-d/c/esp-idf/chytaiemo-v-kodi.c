#include "driver/gpio.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_log.h"

#define TOUCH_GPIO  GPIO_NUM_4   // SIG давача TTP223
#define LED_GPIO    GPIO_NUM_2   // світлодіод плати

static const char *TAG = "ttp223";

void app_main(void) {
    gpio_config_t in = {
        .pin_bit_mask = 1ULL << TOUCH_GPIO,
        .mode         = GPIO_MODE_INPUT,
        .pull_up_en   = GPIO_PULLUP_DISABLE,     // вихід двотактний — підтяжка зайва
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type    = GPIO_INTR_DISABLE,
    };
    ESP_ERROR_CHECK(gpio_config(&in));

    gpio_config_t out = {
        .pin_bit_mask = 1ULL << LED_GPIO,
        .mode         = GPIO_MODE_OUTPUT,
        .pull_up_en   = GPIO_PULLUP_DISABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type    = GPIO_INTR_DISABLE,
    };
    ESP_ERROR_CHECK(gpio_config(&out));

    while (1) {
        bool touched = gpio_get_level(TOUCH_GPIO) == 1;  // активний у 1: дотик = 1
        gpio_set_level(LED_GPIO, touched);
        if (touched) ESP_LOGI(TAG, "дотик!");
        vTaskDelay(pdMS_TO_TICKS(20));
    }
}
