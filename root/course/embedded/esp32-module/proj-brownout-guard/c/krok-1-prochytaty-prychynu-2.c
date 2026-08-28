#include "esp_log.h"
#include "esp_system.h"

static const char *TAG = "boot";

void app_main(void)
{
    esp_reset_reason_t reason = esp_reset_reason();

    switch (reason) {
    case ESP_RST_POWERON:   ESP_LOGI(TAG, "холодний старт"); break;
    case ESP_RST_SW:        ESP_LOGI(TAG, "програмний рестарт"); break;
    case ESP_RST_PANIC:     ESP_LOGW(TAG, "після паніки — глянь core dump"); break;
    case ESP_RST_TASK_WDT:  ESP_LOGW(TAG, "завис таск — сторож скинув"); break;
    case ESP_RST_BROWNOUT:  ESP_LOGE(TAG, "BROWNOUT — живлення просіло!"); break;
    default:                ESP_LOGI(TAG, "скид, причина = %d", (int)reason);
    }

    // …далі — ініціалізація, і лише потім Wi-Fi
}
