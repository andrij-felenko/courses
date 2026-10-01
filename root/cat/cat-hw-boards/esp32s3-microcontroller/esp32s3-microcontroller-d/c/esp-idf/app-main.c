#include "esp_sleep.h"
#include "esp_log.h"
#include "driver/rtc_io.h"

static const char *TAG = "deep_sleep";
static RTC_DATA_ATTR int boot_count = 0; // Збереження змінної в RTC RAM

void app_main(void) {
    boot_count++;
    ESP_LOGI(TAG, "Номер запуску після Deep Sleep: %d", boot_count);

    // Налаштування пробудження за таймером на 10 секунд (10000000 мікросекунд)
    esp_sleep_enable_timer_wakeup(10 * 1000000ULL);
    ESP_LOGI(TAG, "Вхід у режим Deep Sleep на 10 секунд...");

    esp_deep_sleep_start();
}
