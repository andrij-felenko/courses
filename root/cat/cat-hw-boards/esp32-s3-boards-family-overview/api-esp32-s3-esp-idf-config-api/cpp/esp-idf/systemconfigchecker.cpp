#include "esp_system.h"
#include "esp_cpu.h"
#include "esp_log.h"

class SystemConfigChecker {
public:
    static void print_status() {
        uint32_t cpu_freq = esp_cpu_get_freq_mhz();
        ESP_LOGI("SysCheck", "Частота процесора: %lu МГц", cpu_freq);

        if constexpr (IS_SPIRAM_ENABLED) {
            ESP_LOGI("SysCheck", "Апаратний домен PSRAM активний");
        }
    }

private:
    static constexpr bool IS_SPIRAM_ENABLED =
#if defined(CONFIG_SPIRAM)
        true;
#else
        false;
#endif
};
