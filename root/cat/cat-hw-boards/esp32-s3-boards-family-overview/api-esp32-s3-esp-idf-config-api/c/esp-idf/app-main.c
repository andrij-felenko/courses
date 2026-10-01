#include "esp_sleep.h"
#include "driver/gpio.h"
#include "esp_log.h"

static const char *TAG = "DEEP_SLEEP_API";

// Змінна у пам'яті RTC SLOW Memory збереже значення після пробудження
RTC_DATA_ATTR static uint32_t boot_count = 0;

void app_main(void)
{
    boot_count++;
    ESP_LOGI(TAG, "Номер запуску після Deep Sleep: %lu", boot_count);

    // Конфігурація виводу GPIO4 для фіксації логічного рівня
    gpio_config_t io_conf = {
        .pin_bit_mask = (1ULL << GPIO_NUM_4),
        .mode = GPIO_MODE_OUTPUT,
        .pull_up_en = GPIO_PULLUP_DISABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_DISABLE,
    };
    gpio_config(&io_conf);
    gpio_set_level(GPIO_NUM_4, 1);

    // Фіксація стану виводу перед сном
    gpio_hold_en(GPIO_NUM_4);
    gpio_deep_sleep_hold_en();

    // Налаштування таймера пробудження на 10 секунд
    const uint64_t wakeup_time_sec = 10;
    esp_sleep_enable_timer_wakeup(wakeup_time_sec * 1000000ULL);

    ESP_LOGI(TAG, "Вхід у режим Deep Sleep на 10 секунд...");
    esp_deep_sleep_start();
}
