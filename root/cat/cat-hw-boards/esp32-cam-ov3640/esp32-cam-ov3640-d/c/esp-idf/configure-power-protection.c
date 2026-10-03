#include "esp_log.h"
#include "driver/rtc_cntl.h"
#include "soc/rtc_cntl_reg.h"

static const char *TAG = "power_diag";

void configure_power_protection(void) {
    // Перевірка причини попереднього перезавантаження системи
    esp_reset_reason_t reason = esp_reset_reason();
    if (reason == ESP_RST_BROWNOUT) {
        ESP_LOGW(TAG, "Попередній збій викликано просіданням живлення VDD33!");
    }
    
    // Налаштування та діагностика апаратного детектора Brownout
    #if CONFIG_BROWNOUT_DET
    ESP_LOGI(TAG, "Апаратний Brownout Detector активовано на рівні VDD33.");
    #endif
}
