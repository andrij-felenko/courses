#include <stdio.h>
#include "esp_system.h"
#include "esp_log.h"

static const char *TAG = "POWER_MON";

void app_main(void) {
    // Перевірка причини попереднього перезавантаження чипа
    esp_reset_reason_t reason = esp_reset_reason();
    
    if (reason == ESP_RST_BROWNOUT) {
        ESP_LOGW(TAG, "Виявлено апаратне просідання напруги VDD33 (Brown-out Reset)!");
    } else {
        ESP_LOGI(TAG, "Успішний запуск системи, код скидання: %d", reason);
    }
}
