#include "driver/gpio.h"
#include "esp_log.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define SOUND GPIO_NUM_4        // вивід OUT давача
#define LED   GPIO_NUM_2        // світлодіод плати
static const char *TAG = "sound";

static void sound_task(void *arg)
{
    gpio_config_t in = {
        .pin_bit_mask = 1ULL << SOUND,
        .mode = GPIO_MODE_INPUT,
        .pull_up_en = GPIO_PULLUP_DISABLE,   // підтяжка вже стоїть на платі давача
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_DISABLE,
    };
    ESP_ERROR_CHECK(gpio_config(&in));
    ESP_ERROR_CHECK(gpio_set_direction(LED, GPIO_MODE_OUTPUT));

    int64_t last_hit = 0;       // мікросекунди останньої зарахованої події
    unsigned count = 0;

    while (1) {
        int level = gpio_get_level(SOUND);        // 1 = тиша, 0 = гучний звук
        gpio_set_level(LED, level == 0);          // світимо, поки давач бачить звук

        // рахуємо подію, але не частіше ніж раз на 150 мс —
        // інакше один плеск дасть чергу спрацювань
        int64_t now = esp_timer_get_time();
        if (level == 0 && now - last_hit > 150000) {
            last_hit = now;
            ESP_LOGI(TAG, "гучний звук #%u", ++count);
        }
        vTaskDelay(pdMS_TO_TICKS(2));   // щільний цикл, щоб не проґавити імпульс
    }
}

void app_main(void)
{
    xTaskCreate(sound_task, "sound", 3072, NULL, 5, NULL);
}
