#include "driver/gpio.h"
#include "esp_log.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define TILT      GPIO_NUM_4
#define SETTLE_US 30000            // 30 мс: скільки рівень має протриматися

static const char *TAG = "tilt";

void app_main(void) {
    gpio_config_t in = {
        .pin_bit_mask = 1ULL << TILT,
        .mode         = GPIO_MODE_INPUT,
        .pull_up_en   = GPIO_PULLUP_DISABLE,   // підтяжка вже на модулі
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type    = GPIO_INTR_DISABLE,
    };
    ESP_ERROR_CHECK(gpio_config(&in));

    int stable = 1, last_raw = 1;              // 1 = рівно
    int64_t last_change = esp_timer_get_time();
    uint32_t tilts = 0;                        // лічильник справжніх нахилів

    while (1) {
        int raw = gpio_get_level(TILT);        // сире, брязкуче
        if (raw != last_raw) {                 // рівень щойно смикнувся —
            last_change = esp_timer_get_time();// перезапускаємо відлік «тиші»
            last_raw = raw;
        }
        // рівень протримався сталим довше за SETTLE_US → приймаємо його
        if (esp_timer_get_time() - last_change > SETTLE_US && raw != stable) {
            stable = raw;
            if (stable == 0) {                 // перейшли саме в «нахил»
                tilts++;
                ESP_LOGI(TAG, "нахилів: %u", (unsigned)tilts);
            }
        }
        vTaskDelay(pdMS_TO_TICKS(5));          // не займаємо процесор намарно
    }
}
