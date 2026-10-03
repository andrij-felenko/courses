#include "esp_sleep.h"
#include "driver/gpio.h"
#include "esp_log.h"

#define AUDIO_TRIGGER_GPIO GPIO_NUM_4

static const char *TAG = "POWER_MGMT";

void enter_deep_sleep_until_audio(void) {
    ESP_LOGI(TAG, "Налаштування пробудження за пороговим сигналом на GPIO %d...", AUDIO_TRIGGER_GPIO);

    // Налаштовуємо пробудження від зовнішнього апаратного компаратора аудіосигналу (високий рівень)
    esp_sleep_enable_ext0_wakeup(AUDIO_TRIGGER_GPIO, 1);

    ESP_LOGI(TAG, "Перехід пристрою у режим Deep Sleep...");
    esp_deep_sleep_start();
}
