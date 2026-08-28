#include "driver/gpio.h"
#include "esp_log.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define SOUND_GPIO  GPIO_NUM_4      // вивід DO давача
#define LED_GPIO    GPIO_NUM_2      // світлодіод на платі

static const char *TAG = "ky038";

void ky038_task(void *arg) {
    gpio_config_t in = {
        .pin_bit_mask = 1ULL << SOUND_GPIO,
        .mode         = GPIO_MODE_INPUT,
        .pull_up_en   = GPIO_PULLUP_DISABLE,    // DO має підтяжку на платі
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

    int64_t  last_evt = 0;          // мкс останньої зарахованої події
    unsigned count    = 0;          // лічильник гучних подій

    for (;;) {
        int loud = gpio_get_level(SOUND_GPIO);   // 1 = звук понад поріг
        gpio_set_level(LED_GPIO, loud);          // світимо, поки чуємо гучне

        // рахуємо подію не частіше ніж раз на 300 мс (таймер лічить мікросекунди)
        int64_t now = esp_timer_get_time();
        if (loud && now - last_evt > 300000) {
            last_evt = now;
            ESP_LOGI(TAG, "гучно #%u", ++count);
        }
        vTaskDelay(pdMS_TO_TICKS(2));   // щільний цикл, але не з'їдає процесор
    }
}
