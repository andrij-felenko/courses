#include "esp_sleep.h"
#include "driver/gpio.h"
#include "esp_log.h"

namespace DeepSleepManager {
    static const char *TAG = "DEEP_SLEEP_CPP";

    // Збереження лічильника в енергонезалежному домені RTC SLOW
    RTC_DATA_ATTR uint32_t bootCounter = 0;

    void enterSleepWithPinHold(gpio_num_t pin, uint64_t sleepDurationSec) {
        bootCounter++;
        ESP_LOGI(TAG, "Сесія пробудження: %lu", bootCounter);

        gpio_config_t config = {
            .pin_bit_mask = (1ULL << pin),
            .mode = GPIO_MODE_OUTPUT,
            .pull_up_en = GPIO_PULLUP_DISABLE,
            .pull_down_en = GPIO_PULLDOWN_DISABLE,
            .intr_type = GPIO_INTR_DISABLE,
        };
        gpio_config(&config);
        gpio_set_level(pin, 1);

        gpio_hold_en(pin);
        gpio_deep_sleep_hold_en();

        esp_sleep_enable_timer_wakeup(sleepDurationSec * 1000000ULL);
        ESP_LOGI(TAG, "Перехід у Deep Sleep...");
        esp_deep_sleep_start();
    }
}

extern "C" void app_main(void)
{
    DeepSleepManager::enterSleepWithPinHold(GPIO_NUM_4, 10);
}
