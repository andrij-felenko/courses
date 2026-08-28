#include "driver/gpio.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define SOUND GPIO_NUM_4                 // вивід DO давача
static const char *TAG = "sound";

void app_main(void) {
    gpio_config_t io = {
        .pin_bit_mask = 1ULL << SOUND,
        .mode         = GPIO_MODE_INPUT,
        .pull_up_en   = GPIO_PULLUP_DISABLE,    // підтяжка вже на платі давача
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type    = GPIO_INTR_DISABLE,      // поки що чисте опитування
    };
    ESP_ERROR_CHECK(gpio_config(&io));

    int prev = 1;                               // спокій = 1
    while (1) {
        int now = gpio_get_level(SOUND);
        if (prev == 1 && now == 0) {            // спіймали спадний фронт «1→0»
            ESP_LOGI(TAG, "звук!");
        }
        prev = now;
        vTaskDelay(1);   // один такт планувальника; для щільного опитування
                         // підніміть CONFIG_FREERTOS_HZ до 1000 (такт = 1 мс)
    }
}
