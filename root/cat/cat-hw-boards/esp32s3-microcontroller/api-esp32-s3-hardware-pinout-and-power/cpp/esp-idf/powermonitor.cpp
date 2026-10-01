#include <iostream>
#include "esp_system.h"
#include "esp_log.h"

namespace System {
    class PowerMonitor {
    private:
        static constexpr const char* TAG = "POWER_MON";

    public:
        static void check_reset_reason() {
            esp_reset_reason_t reason = esp_reset_reason();
            
            if (reason == ESP_RST_BROWNOUT) {
                ESP_LOGW(TAG, "Спрацював апаратний детектор просідання напруги VDD33!");
            } else {
                ESP_LOGI(TAG, "Нормальний запуск кристала, код скидання: %d", reason);
            }
        }
    };
}

extern "C" void app_main(void) {
    System::PowerMonitor::check_reset_reason();
}
