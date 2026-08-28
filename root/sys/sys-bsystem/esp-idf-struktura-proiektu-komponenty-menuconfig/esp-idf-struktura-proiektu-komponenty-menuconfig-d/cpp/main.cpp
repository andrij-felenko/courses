// main/main.cpp (C++)
#include <iostream>
#include <string_view>
#include <cstdint>
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "sdkconfig.h"

namespace app {

struct Configuration {
    std::string_view ssid{CONFIG_APP_WIFI_SSID};
    uint16_t port{static_cast<uint16_t>(CONFIG_APP_TELEMETRY_PORT)};
    
    static constexpr bool is_power_save_enabled() noexcept {
#if CONFIG_APP_ENABLE_POWER_SAVE
        return true;
#else
        return false;
#endif
    }
};

class SystemController {
public:
    explicit SystemController(const Configuration& config) : config_(config) {}

    void run() const {
        std::cout << "[C++ Node] Ініціалізація точки зв'язку: " << config_.ssid
                  << ", порт: " << config_.port 
                  << ", режим сну: " << (Configuration::is_power_save_enabled() ? "ТАК" : "НІ")
                  << std::endl;
    }

private:
    Configuration config_;
};

} // namespace app

extern "C" void app_main(void) {
    const app::Configuration conf{};
    const app::SystemController controller{conf};
    controller.run();

    while (true) {
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}
