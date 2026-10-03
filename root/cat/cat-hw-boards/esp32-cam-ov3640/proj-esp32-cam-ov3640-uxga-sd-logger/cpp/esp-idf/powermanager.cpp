#include "esp_log.h"
#include "driver/gpio.h"
#include "esp_sleep.hpp"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

class PowerManager {
private:
    static constexpr gpio_num_t pwr_gpio = GPIO_NUM_13;
    static constexpr const char* TAG = "PowerMgrCPP";

public:
    static void init() {
        gpio_config_t io_conf{};
        io_conf.pin_bit_mask = (1ULL << pwr_gpio);
        io_conf.mode = GPIO_MODE_OUTPUT;
        gpio_config(&io_conf);
    }

    static void enablePeripherals() {
        gpio_set_level(pwr_gpio, 0);
        ESP_LOGI(TAG, "Живлення OV3640 та SDMMC увімкнено");
        vTaskDelay(pdMS_TO_TICKS(50));
    }

    static void disablePeripherals() {
        gpio_set_level(pwr_gpio, 1);
        ESP_LOGI(TAG, "Живлення периферії вимкнено");
    }
};

extern "C" void app_main() {
    PowerManager::init();
    PowerManager::enablePeripherals();

    // Запуски фотореєстратора
    // ...

    PowerManager::disablePeripherals();
    esp_sleep_enable_timer_wakeup(60 * 1000000ULL);
    esp_deep_sleep_start();
}
