#include "esp_pm.h"
#include "esp_log.h"

void init_power_management() {
    esp_pm_config_t pm_config = {
        .max_freq_mhz = 240,
        .min_freq_mhz = 40,
        .light_sleep_enable = true
    };
    
    // Ініціалізація автоматичного керування живленням
    esp_err_t err = esp_pm_configure(&pm_config);
    if (err != ESP_OK) {
        ESP_LOGE("PM", "Помилка конфігурації живлення: %s", esp_err_to_name(err));
    }
}
