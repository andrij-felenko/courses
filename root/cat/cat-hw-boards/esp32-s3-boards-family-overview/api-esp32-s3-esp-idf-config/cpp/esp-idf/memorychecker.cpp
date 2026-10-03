#include <iostream>
#include "esp_psram.h"
#include "esp_log.h"

class MemoryChecker {
private:
    static constexpr const char *TAG = "PSRAM_INIT";
public:
    static void check() {
        if (esp_psram_is_initialized()) {
            size_t size = esp_psram_get_size();
            ESP_LOGI(TAG, "Успішно ініціалізовано зовнішню PSRAM. Обсяг: %zu байт", size);
        } else {
            ESP_LOGE(TAG, "Помилка ініціалізації PSRAM! Перевірте налаштування sdkconfig.");
        }
    }
};
