#include "esp_psram.h"
#include "esp_heap_caps.h"
#include "esp_log.h"

void app_main(void) {
  if (esp_psram_is_initialized())
    ESP_LOGI("psram", "PSRAM є: %u КБ усього, %u КБ вільно",
             (unsigned)(esp_psram_get_size() / 1024),
             (unsigned)(heap_caps_get_free_size(MALLOC_CAP_SPIRAM) / 1024));
  else
    ESP_LOGW("psram", "PSRAM не знайдено: увімкни CONFIG_SPIRAM у menuconfig");
}
