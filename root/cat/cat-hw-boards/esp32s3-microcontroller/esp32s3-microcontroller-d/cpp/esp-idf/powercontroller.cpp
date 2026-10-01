#include <cstdio>
#include <cstdint>
#include "esp_sleep.h"
#include "esp_log.h"

static const char *TAG = "POWER_MGMT_CPP";

class PowerController {
public:
    static void configureAndSleep(uint64_t seconds) {
        ESP_LOGI(TAG, "Конфігурація сну на %llu с", seconds);
        esp_sleep_enable_timer_wakeup(seconds * 1000000ULL);
        esp_deep_sleep_start();
    }
};
