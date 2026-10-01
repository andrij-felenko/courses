#include "esp_system.h"
#include "esp_cpu.h"
#include "esp_log.h"

static const char *TAG = "sys_config";

void check_system_configuration(void) {
    uint32_t cpu_freq = esp_cpu_get_freq_mhz();
    ESP_LOGI(TAG, "Частота ядра CPU: %lu МГц", cpu_freq);

#if defined(CONFIG_SPIRAM)
    ESP_LOGI(TAG, "Підтримка зовнішньої PSRAM увімкнена у sdkconfig");
#else
    ESP_LOGW(TAG, "Зовнішня PSRAM вимкнена або не знайдена");
#endif
}
